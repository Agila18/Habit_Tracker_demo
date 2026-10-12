# 🌱 Habit Tracker Lite

A lightweight, beginner-friendly, and responsive web application designed to help you build, track, and celebrate daily habits. Built with **Python 3.12+**, **Flask**, **SQLite**, and **Vanilla JavaScript**.

---

## 📸 Features Overview

- **Daily Habit Tracking**: Create habits with a name and optional description.
- **Toggle Today's Completion**: Mark habits as completed for today or undo completion with one click.
- **Dynamic Progress Bar & Metrics**: Visual celebration of your daily consistency, showing total habits, habits completed today, and completion percentage.
- **Duplicate Prevention**: Guaranteed data integrity preventing duplicate completion records for the same habit and date.
- **Habit History & Totals**: Track total completions for every habit.
- **Delete Confirmation Modal**: Protect against accidental habit deletion with clean modal prompts.
- **Polished, Responsive UI**: Card-based interface with smooth micro-interactions, character counters, skeleton loading states, empty states, and toast notifications.
- **Zero External UI Frameworks**: Pure Vanilla CSS and JavaScript—no Node.js, React, or npm required.
- **Automated Test Suite**: Comprehensive tests covering all API endpoints and database operations using an isolated temporary test database.

---

## 📂 Project Structure

```text
habit-tracker-lite/
├── app.py                  # Flask backend & SQLite database layer
├── requirements.txt        # Python package dependencies (Flask, pytest)
├── .gitignore              # Ignores database files, caches, and virtual envs
├── README.md               # Beginner-friendly guide and documentation
├── templates/
│   └── index.html          # Semantic HTML5 template with progress dashboard
├── static/
│   ├── css/
│   │   └── style.css       # Responsive, modern Vanilla CSS styling
│   └── js/
│       └── app.js          # Vanilla JavaScript handling API calls & dynamic UI
└── tests/
    ├── __init__.py         # Test package marker
    └── test_app.py         # Automated test suite (15 unit & integration tests)
```

---

## 🛠️ Step-by-Step Beginner Setup Guide

### 1. Install Python on Windows

1. Download the official installer from [python.org](https://www.python.org/downloads/). Choose **Python 3.12 or newer**.
2. Run the installer `.exe` file.
3. ⚠️ **Important:** On the very first screen of the installer, check the box that says:
   **☑ "Add python.exe to PATH"**.
4. Click **Install Now** and wait for the setup to finish.
5. Open **PowerShell** or **Command Prompt** and verify the installation:
   ```powershell
   python --version
   ```
   *Expected output: `Python 3.12.x` (or newer)*

---

### 2. Create and Activate a Virtual Environment

A virtual environment is an isolated workspace for your project so its dependencies do not interfere with other Python projects on your computer.

1. Navigate to the project folder:
   ```powershell
   cd habit-tracker-lite
   ```

2. Create a virtual environment named `venv`:
   ```powershell
   python -m venv venv
   ```
   - `python -m venv`: Tells Python to run the built-in virtual environment module.
   - `venv`: The name of the folder where the virtual environment files will be stored.

3. Activate the virtual environment:
   - On **Windows PowerShell**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
     *(If you see an execution policy error, see the Troubleshooting section below.)*
   - On **Windows Command Prompt (cmd.exe)**:
     ```cmd
     venv\Scripts\activate.bat
     ```
   - On **macOS / Linux**:
     ```bash
     source venv/bin/activate
     ```

   *When activated, your terminal prompt will show `(venv)` at the beginning of the line.*

---

### 3. Install Requirements

With your virtual environment activated, install the required packages:

```powershell
pip install -r requirements.txt
```
- `pip`: Python's package manager.
- `install -r requirements.txt`: Reads the list of dependencies in `requirements.txt` (Flask and pytest) and downloads them into your virtual environment.

---

### 4. Run the Application Locally

Start the local Flask development server:

```powershell
python app.py
```

You should see output similar to:
```text
Starting Habit Tracker Lite on http://127.0.0.1:5000 ...
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

The SQLite database file (`habits.db`) will be automatically created inside a `data/` folder the first time you run the app.

---

### 5. Open the Application in Your Browser

Open your favorite web browser (Chrome, Edge, Firefox, Brave) and navigate to:

👉 **[http://localhost:5000](http://localhost:5000)** or **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

You can now:
- Type a habit name (e.g., *"Drink 2L Water"*) and click **Add Habit**.
- Click **✓ Mark Done** to complete it for today. Watch the progress bar fill up!
- Click **↩ Undo** to revert completion.
- Click the trash icon 🗑️ to delete a habit with confirmation.

---

### 6. Run Automated Tests

To ensure everything works as expected, run the automated test suite. Tests automatically run against a temporary in-memory/isolated SQLite database that never touches your actual habits.

You can use either Python's built-in `unittest` runner or `pytest`:

**Option A — Built-in unittest runner (no extra tools needed):**
```powershell
python -m unittest tests/test_app.py
```

**Option B — Using pytest:**
```powershell
python -m pytest
```

*Expected output:*
```text
...............
----------------------------------------------------------------------
Ran 15 tests in 0.98s

OK
```

All 15 tests should pass.

---

### 7. Initialize Git and Push to GitHub

Here is how to put your project under Git version control and publish it to GitHub:

1. **Initialize Git** in the project directory:
   ```powershell
   git init
   ```
   *Creates a local `.git` repository folder.*

2. **Stage all files**:
   ```powershell
   git add .
   ```
   *Stages files for commit. Notice that your `.gitignore` will automatically exclude `.db` files, `venv/`, and `__pycache__`.*

3. **Make your initial commit**:
   ```powershell
   git commit -m "Initial commit: Habit Tracker Lite application"
   ```

4. **Create a new repository on GitHub**:
   - Go to [github.com](https://github.com) and log in.
   - Click the **+** icon in the top right corner and choose **New repository**.
   - Name your repository (e.g., `habit-tracker-lite`).
   - Leave "Add a README", ".gitignore", and "license" unchecked (we already have them).
   - Click **Create repository**.

5. **Link your local repository to GitHub and push**:
   ```powershell
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/habit-tracker-lite.git
   git push -u origin main
   ```
   *(Replace `YOUR_USERNAME` with your actual GitHub username).*

---

### 8. Clone the Repository into a Separate Local Folder

To verify that anyone can clone and run your project from scratch:

1. Open a new PowerShell terminal and navigate to a separate directory (e.g. `C:\Projects`):
   ```powershell
   cd C:\Projects
   ```

2. Clone your GitHub repository:
   ```powershell
   git clone https://github.com/YOUR_USERNAME/habit-tracker-lite.git
   ```

3. Enter the cloned directory:
   ```powershell
   cd habit-tracker-lite
   ```

4. Set up the virtual environment and install packages:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

5. Run the application:
   ```powershell
   python app.py
   ```

---

## 📡 REST API Reference

The backend provides the following endpoints:

| Method | Endpoint | Description | Status Codes |
|---|---|---|---|
| `GET` | `/` | Renders the HTML user interface | `200` |
| `GET` | `/health` | Returns health status JSON payload | `200` |
| `GET` | `/api/habits` | Lists all habits with today's status & statistics | `200` |
| `POST` | `/api/habits` | Adds a new habit (`name` required, `description` optional) | `201`, `400` |
| `PATCH` | `/api/habits/<id>/complete` | Toggles today's completion for a habit (idempotent, no duplicates) | `200`, `404` |
| `DELETE` | `/api/habits/<id>` | Deletes a habit and all associated completion history | `200`, `404` |

### Sample JSON Requests & Responses

#### Add a Habit (`POST /api/habits`)
**Request Body:**
```json
{
  "name": "Read 20 pages",
  "description": "Read before going to sleep"
}
```

**Response (`201 Created`):**
```json
{
  "message": "Habit created successfully!",
  "habit": {
    "id": 1,
    "name": "Read 20 pages",
    "description": "Read before going to sleep",
    "created_at": "2026-10-12 16:30:00",
    "completed_today": false,
    "total_completions": 0
  }
}
```

#### Toggle Completion (`PATCH /api/habits/1/complete`)
**Response (`200 OK`):**
```json
{
  "habit_id": 1,
  "completed_today": true,
  "message": "Great job! Marked 'Read 20 pages' as completed for today!",
  "total_completions": 1
}
```

---

## 🔧 Troubleshooting Common Errors

### 1. PowerShell Script Execution Error (`Activate.ps1 cannot be loaded`)
**Cause:** Windows PowerShell disables running unsigned scripts by default for security.  
**Fix:** Run this one-time command in PowerShell to allow scripts for your current user:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then run `.\venv\Scripts\Activate.ps1` again.

---

### 2. `python` or `pip` is not recognized
**Cause:** Python was installed without checking "Add python.exe to PATH".  
**Fix:**
1. Rerun the Python installer from [python.org](https://www.python.org).
2. Choose **Modify** or **Reinstall**.
3. Ensure **"Add python.exe to PATH"** is checked.
4. Close and reopen PowerShell.

---

### 3. Port 5000 is already in use (`Address already in use`)
**Cause:** Another application or another instance of Flask is already running on port 5000.  
**Fix:**
- Find and close the other terminal window running the app, or
- Change the port in `app.py` line 372:
  ```python
  app.run(host="127.0.0.1", port=5001, debug=True)
  ```
  Then visit `http://localhost:5001`.

---

### 4. Database Locked or Permission Error on Windows
**Cause:** A database browser or background process has an exclusive lock on `data/habits.db`.  
**Fix:**
- Close any external SQLite viewers (e.g., DB Browser for SQLite) before deleting or resetting data.
- The app automatically closes connections at the end of each request to avoid locks.

---

## 📄 License
This project is open source and available under the [MIT License](https://opensource.org/licenses/MIT).
