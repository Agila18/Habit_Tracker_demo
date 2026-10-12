"""
Automated Test Suite for Habit Tracker Lite
Tests backend API endpoints, input validation, and database operations
using an isolated temporary SQLite database for each test run.
"""

import os
import sys
import tempfile
import unittest

# Ensure the parent directory is on the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, get_db


class HabitTrackerTestCase(unittest.TestCase):
    """Test cases for Habit Tracker Lite Flask application."""

    def setUp(self):
        """Create a fresh temporary database and application instance for each test."""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE": self.db_path,
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up and remove the temporary database file."""
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            try:
                os.unlink(self.db_path)
            except PermissionError:
                pass

    # -------------------------------------------------------------
    # 1. Page and Health Check Tests
    # -------------------------------------------------------------

    def test_health_check(self):
        """GET /health should return 200 OK and healthy status JSON."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["app"], "Habit Tracker Lite")

    def test_home_page(self):
        """GET / should return 200 OK and render HTML containing app title."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Habit Tracker Lite", response.data)

    # -------------------------------------------------------------
    # 2. Habit Listing Tests
    # -------------------------------------------------------------

    def test_list_habits_empty(self):
        """GET /api/habits on an empty database should return empty list and zeroed stats."""
        response = self.client.get("/api/habits")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["habits"], [])
        self.assertEqual(data["stats"]["total"], 0)
        self.assertEqual(data["stats"]["completed_today"], 0)
        self.assertEqual(data["stats"]["completion_percentage"], 0)

    # -------------------------------------------------------------
    # 3. Habit Creation Tests
    # -------------------------------------------------------------

    def test_create_habit_success(self):
        """POST /api/habits with valid data should return 201 Created and the new habit."""
        payload = {
            "name": "Drink 2L Water",
            "description": "Stay hydrated throughout the workday",
        }
        response = self.client.post("/api/habits", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("habit", data)
        habit = data["habit"]
        self.assertEqual(habit["name"], "Drink 2L Water")
        self.assertEqual(habit["description"], "Stay hydrated throughout the workday")
        self.assertFalse(habit["completed_today"])
        self.assertEqual(habit["total_completions"], 0)

        # Verify it now appears in the list
        list_resp = self.client.get("/api/habits")
        list_data = list_resp.get_json()
        self.assertEqual(len(list_data["habits"]), 1)
        self.assertEqual(list_data["stats"]["total"], 1)

    def test_create_habit_without_description(self):
        """POST /api/habits with only a name should succeed with an empty description."""
        payload = {"name": "Morning Meditation"}
        response = self.client.post("/api/habits", json=payload)
        self.assertEqual(response.status_code, 201)
        habit = response.get_json()["habit"]
        self.assertEqual(habit["name"], "Morning Meditation")
        self.assertEqual(habit["description"], "")

    def test_create_habit_validation_missing_name(self):
        """POST /api/habits without a name should return 400 Bad Request."""
        response = self.client.post("/api/habits", json={"description": "No name provided"})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)

    def test_create_habit_validation_empty_whitespace_name(self):
        """POST /api/habits with whitespace-only name should return 400 Bad Request."""
        response = self.client.post("/api/habits", json={"name": "    "})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)

    def test_create_habit_validation_name_too_long(self):
        """POST /api/habits with name > 100 characters should return 400 Bad Request."""
        payload = {"name": "A" * 101}
        response = self.client.post("/api/habits", json=payload)
        self.assertEqual(response.status_code, 400)

    def test_create_habit_validation_description_too_long(self):
        """POST /api/habits with description > 300 characters should return 400 Bad Request."""
        payload = {"name": "Reading", "description": "B" * 301}
        response = self.client.post("/api/habits", json=payload)
        self.assertEqual(response.status_code, 400)

    # -------------------------------------------------------------
    # 4. Completion Toggle & Undo Tests
    # -------------------------------------------------------------

    def test_toggle_habit_completion_and_undo(self):
        """PATCH /api/habits/<id>/complete toggles today's completion on then off."""
        # 1. Create a habit
        create_resp = self.client.post("/api/habits", json={"name": "Daily Journal"})
        habit_id = create_resp.get_json()["habit"]["id"]

        # 2. Mark complete
        toggle1 = self.client.patch(f"/api/habits/{habit_id}/complete")
        self.assertEqual(toggle1.status_code, 200)
        data1 = toggle1.get_json()
        self.assertTrue(data1["completed_today"])
        self.assertEqual(data1["total_completions"], 1)

        # Verify stats reflect completed
        list1 = self.client.get("/api/habits").get_json()
        self.assertEqual(list1["stats"]["completed_today"], 1)
        self.assertEqual(list1["stats"]["completion_percentage"], 100.0)

        # 3. Toggle again to undo completion
        toggle2 = self.client.patch(f"/api/habits/{habit_id}/complete")
        self.assertEqual(toggle2.status_code, 200)
        data2 = toggle2.get_json()
        self.assertFalse(data2["completed_today"])
        self.assertEqual(data2["total_completions"], 0)

        # Verify stats reflect undone
        list2 = self.client.get("/api/habits").get_json()
        self.assertEqual(list2["stats"]["completed_today"], 0)
        self.assertEqual(list2["stats"]["completion_percentage"], 0.0)

    def test_toggle_nonexistent_habit(self):
        """PATCH /api/habits/99999/complete should return 404 Not Found."""
        response = self.client.patch("/api/habits/99999/complete")
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("error", data)

    def test_prevent_duplicate_completions_for_same_date(self):
        """Database constraint prevents duplicate completion records for same habit and date."""
        create_resp = self.client.post("/api/habits", json={"name": "Study Python"})
        habit_id = create_resp.get_json()["habit"]["id"]

        # Toggle once -> completed
        resp = self.client.patch(f"/api/habits/{habit_id}/complete")
        self.assertEqual(resp.status_code, 200)

        # Inspect database directly
        with self.app.app_context():
            db = get_db()
            rows = db.execute(
                "SELECT COUNT(*) as count FROM completions WHERE habit_id = ?",
                (habit_id,),
            ).fetchone()
            self.assertEqual(rows["count"], 1)

    # -------------------------------------------------------------
    # 5. Habit Deletion Tests
    # -------------------------------------------------------------

    def test_delete_habit_success(self):
        """DELETE /api/habits/<id> should return 200 OK and remove habit and completions."""
        create_resp = self.client.post("/api/habits", json={"name": "Temporary Task"})
        habit_id = create_resp.get_json()["habit"]["id"]

        # Mark completed first
        self.client.patch(f"/api/habits/{habit_id}/complete")

        # Delete habit
        del_resp = self.client.delete(f"/api/habits/{habit_id}")
        self.assertEqual(del_resp.status_code, 200)
        data = del_resp.get_json()
        self.assertEqual(data["deleted_id"], habit_id)

        # Verify it no longer exists
        list_resp = self.client.get("/api/habits")
        list_data = list_resp.get_json()
        self.assertEqual(len(list_data["habits"]), 0)

        # Verify completions table has no orphan rows
        with self.app.app_context():
            db = get_db()
            rows = db.execute(
                "SELECT COUNT(*) as count FROM completions WHERE habit_id = ?",
                (habit_id,),
            ).fetchone()
            self.assertEqual(rows["count"], 0)

    def test_delete_nonexistent_habit(self):
        """DELETE /api/habits/99999 should return 404 Not Found."""
        response = self.client.delete("/api/habits/99999")
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("error", data)

    # -------------------------------------------------------------
    # 6. Overall Statistics Calculation Test
    # -------------------------------------------------------------

    def test_multiple_habits_statistics(self):
        """Verify total, completed count, and percentage calculation with multiple habits."""
        # Create 4 habits
        self.client.post("/api/habits", json={"name": "Habit 1"})
        h2 = self.client.post("/api/habits", json={"name": "Habit 2"}).get_json()["habit"]["id"]
        h3 = self.client.post("/api/habits", json={"name": "Habit 3"}).get_json()["habit"]["id"]
        self.client.post("/api/habits", json={"name": "Habit 4"})

        # Complete 2 of them (50%)
        self.client.patch(f"/api/habits/{h2}/complete")
        self.client.patch(f"/api/habits/{h3}/complete")

        response = self.client.get("/api/habits")
        stats = response.get_json()["stats"]
        self.assertEqual(stats["total"], 4)
        self.assertEqual(stats["completed_today"], 2)
        self.assertEqual(stats["completion_percentage"], 50.0)


if __name__ == "__main__":
    unittest.main()
