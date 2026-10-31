from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from pathlib import Path
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'encryptionKey'

BASE = Path(__file__).parent
DB_FILE = BASE / "db.json"
USERDATA_FILE = BASE / "userdata.json"

global users
global userdata
@app.route('/')
def home():
    with open(DB_FILE, "r") as f:
        db = json.load(f)
    with open(USERDATA_FILE, "r") as g:
        userdata = json.load(g)
    return render_template('home.html')


def progress():
    with open(USERDATA_FILE, "r") as f:
        userdata = json.load(f)

    user_id = session.get("userId")

    for user in userdata.get("users", []):
        if str(user.get("id")) == str(user_id):
            goal_progress = []

            for goal in user.get("goals", []):
                tasks = goal.get("task", [])
                total_tasks = len(tasks)
                completed_tasks = sum(
                    1 for task in tasks
                    if task.get("isCompleted", False)
                )
                percentage = (
                    (completed_tasks / total_tasks) * 100
                    if total_tasks else 0
                )
                goal_progress.append({
                    "name": goal.get("name", "Untitled Goal"),
                    "completedTask": completed_tasks,
                    "totalTask": total_tasks,
                    "percentage": round(percentage, 2)
                })
            return goal_progress
    return []

            
            
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        with open(DB_FILE, "r") as f:
            db = json.load(f)
        with open(USERDATA_FILE, "r") as g:
            userdata = json.load(g)
        
        for u in db["users"]:
            if u["username"] == username and u["password"] == password:
                session['user'] = u["username"]
                session['userId'] = u["id"]
                session['name'] = u.get("name", u["username"])
                session['email'] = u.get("email", u["username"])
                
                return redirect(url_for('dashboard'))
            
        return redirect(url_for('login'))

    return render_template('login.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not name or not email or not username or not password:
            flash("All fields are required")
            return redirect(url_for('signup'))

        with open(DB_FILE, "r") as f:
            db = json.load(f)

        with open(USERDATA_FILE, "r") as f:
            userdata = json.load(f)

        for u in db["users"]:
            if u["username"].lower() == username.lower():
                flash("Username already taken")
                return redirect(url_for('signup'))

        user_id = "u_" + str(len(db["users"]) + 1).zfill(3)

        new_user = {
            "id": user_id,
            "name": name,
            "email": email,
            "username": username,
            "password": password,
            "role": "user",
            "status": "active",
            "createdAt": datetime.now().astimezone().isoformat(timespec="seconds")
        }

        new_user_data = {
            "id": user_id,
            "goals": [],
            "Achievements": [],
            "projects": []
        }

        db["users"].append(new_user)
        userdata["users"].append(new_user_data)

        with open(DB_FILE, "w") as f:
            json.dump(db, f, indent=4)

        with open(USERDATA_FILE, "w") as f:
            json.dump(userdata, f, indent=4)

        flash("Account created. Please login.")
        return redirect(url_for('login'))

    return render_template('signup.html')



@app.route('/dashboard')
def dashboard():
    if not session.get('user'):
        return redirect(url_for('login'))

    with open(USERDATA_FILE, "r") as f:
        userdata = json.load(f)

    user_data = None

    for u in userdata.get("users", []):
        if str(u.get("id")) == str(session.get("userId")):
            user_data = u
            break

    if user_data is None:
        return redirect(url_for('login'))

    all_tasks = [
        task
        for goal in user_data.get("goals", [])
        for task in goal.get("task", [])
    ]

    data = {
        "name": session.get("name", session.get("user")),
        "Achievements": user_data.get("Achievements", []),
        "progress": all_tasks,
        "goal_progress": progress()
    }

    return render_template(
        "dashboard.html",
        user=data,
        userdata=user_data
    )


@app.route('/projects', methods=['GET', 'POST'])
def projects():
    if not session.get('user'):
        return redirect(url_for('login'))
    
    with open(DB_FILE, "r") as f:
        db = json.load(f)

    with open(USERDATA_FILE, "r") as f:
        userdata = json.load(f)

    user_id = session.get('userId')
    name = session.get('name')
    
    user_exists = any(
        str(u["id"]) == str(user_id)
        for u in db["users"]
    )
    if not user_exists:
        return redirect(url_for('login'))
    user_data = None
    for u in userdata["users"]:
        if str(u["id"]) == str(user_id):
            user_data = u
            break

    if user_data is None:
        return redirect(url_for('login'))
    
    user_data.setdefault("projects", [])
    if request.method == 'POST':
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        link = request.form.get("link", "").strip()

        if not name or not description:
            return redirect(url_for('projects'))
        new_project = {
            "id": str(len(user_data["projects"]) + 1),
            "name": name,
            "description": description,
            "link": link
        }
        user_data["projects"].append(new_project)

        with open(USERDATA_FILE, "w") as f:
            json.dump(userdata, f, indent=4)

        return redirect(url_for('projects'))
    projects = user_data.get("projects", [])
    return render_template( 'projects.html', projects=projects )


@app.route('/profile')
def profile():
    if not session.get('user'):
        return redirect(url_for('login'))

    with open(USERDATA_FILE, "r") as f:
        userdata = json.load(f)

    user_id = session.get("userId")
    user = None

    for u in userdata.get("users", []):
        if str(u.get("id")) == str(user_id):
            user = u
            break

    if user is None:
        return redirect(url_for('login'))

    projects = user.get("projects", [])
    goals = user.get("goals", [])
    achievements = user.get("Achievements", [])

    return render_template(
        'profile.html',
        user=user,
        projects=projects,
        goals=goals,
        achievements=achievements,
        totalProjects=len(projects),
        totalGoals=len(goals),
        totalAchievements=len(achievements)
    )
     

@app.route("/goals")
def goals():

    with open(USERDATA_FILE, "r") as f:
        userdata = json.load(f)

    user_id = session.get("userId")

    user_data = {}

    for user in userdata["users"]:
        if user["id"] == user_id:
            user_data = user
            break

    goals = user_data.get("goals", [])

    total_goals = len(goals)
    completed_goals = 0
    active_goals = 0

    for goal in goals:
        if goal.get("isCompleted") == True:
            completed_goals += 1
        else:
            active_goals += 1

        total = len(goal["task"])
        completed = 0

        for task in goal["task"]:
            if task["isCompleted"]:
                completed += 1

        if total > 0:
            goal["progress"] = int(completed / total * 100)
        else:
            goal["progress"] = 0

        goal["next_tasks"] = []

        for task in goal["task"]:
            if not task["isCompleted"]:
                goal["next_tasks"].append(task)

    return render_template(
        "goals.html",
        goals=goals,
        total_goals=total_goals,
        completed_goals=completed_goals,
        active_goals=active_goals,
        task = task 
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)