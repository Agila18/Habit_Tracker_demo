"""
Habit Tracker Lite - Flask Application
A beginner-friendly, clean, and responsive habit tracking web application.
"""

import os
import sqlite3
from datetime import date, datetime, timezone
from flask import Flask, current_app, g, jsonify, render_template, request


def get_db():
    """
    Open a new database connection if there is none yet for the
    current application context.
    """
    if "db" not in g:
        db_path = current_app.config["DATABASE"]

        # Ensure parent directory exists for file-based databases
        if db_path != ":memory:":
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)

        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        # Enable foreign key constraint support in SQLite
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db


def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Initialize the SQLite database schema if tables do not exist."""
    db_path = app.config["DATABASE"]
    if db_path != ":memory:":
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    with app.app_context():
        db = get_db()
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                completed_date TEXT NOT NULL,
                FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE,
                UNIQUE(habit_id, completed_date)
            );
            """
        )
        db.commit()


def compute_stats(habits):
    """
    Helper function to calculate today's completion stats.
    Returns total count, completed today count, and completion percentage.
    """
    total = len(habits)
    completed_today = sum(1 for h in habits if h.get("completed_today"))
    percentage = round((completed_today / total * 100), 1) if total > 0 else 0
    return {
        "total": total,
        "completed_today": completed_today,
        "completion_percentage": percentage,
    }


def create_app(test_config=None):
    """
    Application factory for Habit Tracker Lite.
    Allows easy configuration for both development and automated testing.
    """
    app = Flask(__name__, instance_relative_config=True)

    # Default application configuration
    default_db_path = os.path.join(app.root_path, "data", "habits.db")
    app.config.from_mapping(
        SECRET_KEY="habit-tracker-dev-key",
        DATABASE=default_db_path,
    )

    if test_config is not None:
        app.config.update(test_config)

    app.teardown_appcontext(close_db)

    # Initialize the database
    init_db(app)

    # -------------------------------------------------------------
    # FRONTEND ROUTES
    # -------------------------------------------------------------

    @app.route("/")
    def index():
        """Render the main single-page habit tracker interface."""
        return render_template("index.html")

    # -------------------------------------------------------------
    # API ROUTES
    # -------------------------------------------------------------

    @app.route("/health", methods=["GET"])
    def health():
        """Health check endpoint returning system status."""
        return jsonify(
            {
                "status": "healthy",
                "app": "Habit Tracker Lite",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ), 200

    @app.route("/api/habits", methods=["GET"])
    def list_habits():
        """
        List all habits ordered by creation date, including today's
        completion status and overall completion count.
        """
        db = get_db()
        today = date.today().isoformat()

        cursor = db.execute(
            """
            SELECT 
                h.id, 
                h.name, 
                h.description, 
                h.created_at,
                CASE WHEN c.id IS NOT NULL THEN 1 ELSE 0 END AS completed_today,
                (SELECT COUNT(*) FROM completions WHERE habit_id = h.id) AS total_completions
            FROM habits h
            LEFT JOIN completions c 
                ON h.id = c.habit_id AND c.completed_date = ?
            ORDER BY h.id DESC
            """,
            (today,),
        )
        rows = cursor.fetchall()

        habits = []
        for row in rows:
            habits.append(
                {
                    "id": row["id"],
                    "name": row["name"],
                    "description": row["description"] or "",
                    "created_at": row["created_at"],
                    "completed_today": bool(row["completed_today"]),
                    "total_completions": row["total_completions"],
                }
            )

        stats = compute_stats(habits)
        return jsonify({"habits": habits, "stats": stats}), 200

    @app.route("/api/habits", methods=["POST"])
    def add_habit():
        """
        Create a new habit.
        Validates the habit name and optional description.
        """
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return (
                jsonify(
                    {"error": "Invalid request. JSON request body is required."}
                ),
                400,
            )

        name = data.get("name")
        description = data.get("description", "")

        # Validate habit name
        if not name or not isinstance(name, str):
            return (
                jsonify(
                    {
                        "error": "Habit name is required and must be text."
                    }
                ),
                400,
            )

        name = name.strip()
        if len(name) < 1 or len(name) > 100:
            return (
                jsonify(
                    {
                        "error": "Habit name must be between 1 and 100 characters."
                    }
                ),
                400,
            )

        # Validate description (optional)
        if description is None:
            description = ""
        elif not isinstance(description, str):
            return jsonify({"error": "Description must be text."}), 400
        else:
            description = description.strip()
            if len(description) > 300:
                return (
                    jsonify(
                        {"error": "Description must not exceed 300 characters."}
                    ),
                    400,
                )

        created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        db = get_db()
        cursor = db.execute(
            "INSERT INTO habits (name, description, created_at) VALUES (?, ?, ?)",
            (name, description, created_at),
        )
        db.commit()
        new_id = cursor.lastrowid

        new_habit = {
            "id": new_id,
            "name": name,
            "description": description,
            "created_at": created_at,
            "completed_today": False,
            "total_completions": 0,
        }

        return jsonify({"habit": new_habit, "message": "Habit created successfully!"}), 201

    @app.route("/api/habits/<int:habit_id>/complete", methods=["PATCH"])
    def toggle_complete(habit_id):
        """
        Toggle today's completion for a habit.
        If already completed today, removes the completion (undo).
        If not yet completed today, records today's completion.
        Guarantees no duplicate records for the same habit and date.
        """
        db = get_db()
        today = date.today().isoformat()

        # Check if habit exists
        habit = db.execute("SELECT id, name FROM habits WHERE id = ?", (habit_id,)).fetchone()
        if habit is None:
            return jsonify({"error": f"Habit with ID {habit_id} not found."}), 404

        # Check if completed today
        existing = db.execute(
            "SELECT id FROM completions WHERE habit_id = ? AND completed_date = ?",
            (habit_id, today),
        ).fetchone()

        if existing:
            # Undo completion
            db.execute(
                "DELETE FROM completions WHERE habit_id = ? AND completed_date = ?",
                (habit_id, today),
            )
            db.commit()
            completed_today = False
            message = f"Undid completion for '{habit['name']}'."
        else:
            # Mark completed (prevent duplicate via INSERT OR IGNORE)
            db.execute(
                "INSERT OR IGNORE INTO completions (habit_id, completed_date) VALUES (?, ?)",
                (habit_id, today),
            )
            db.commit()
            completed_today = True
            message = f"Great job! Marked '{habit['name']}' as completed for today!"

        # Fetch current total completions for this habit
        total_cursor = db.execute(
            "SELECT COUNT(*) as count FROM completions WHERE habit_id = ?",
            (habit_id,),
        ).fetchone()
        total_completions = total_cursor["count"] if total_cursor else 0

        return (
            jsonify(
                {
                    "message": message,
                    "habit_id": habit_id,
                    "completed_today": completed_today,
                    "total_completions": total_completions,
                }
            ),
            200,
        )

    @app.route("/api/habits/<int:habit_id>", methods=["DELETE"])
    def delete_habit(habit_id):
        """
        Delete a habit and all associated completion history.
        """
        db = get_db()

        # Verify habit exists
        habit = db.execute("SELECT id, name FROM habits WHERE id = ?", (habit_id,)).fetchone()
        if habit is None:
            return jsonify({"error": f"Habit with ID {habit_id} not found."}), 404

        # Delete habit (completions cascade automatically via foreign key)
        db.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        # Explicit delete on completions as safety measure
        db.execute("DELETE FROM completions WHERE habit_id = ?", (habit_id,))
        db.commit()

        return (
            jsonify(
                {
                    "message": f"Habit '{habit['name']}' was successfully deleted.",
                    "deleted_id": habit_id,
                }
            ),
            200,
        )

    # -------------------------------------------------------------
    # ERROR HANDLERS
    # -------------------------------------------------------------

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Resource not found"}), 404
        return render_template("index.html"), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad request"}), 400

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "An internal server error occurred"}), 500

    return app


# Application entry point for local execution
app = create_app()

if __name__ == "__main__":
    # Run locally on port 5000 in debug mode
    print("Starting Habit Tracker Lite on http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True)
