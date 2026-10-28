from flask import Flask, render_template, request, redirect, url_for, session
import secrets
import json
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

global user 
   
# 1. Home page
@app.route('/')
def index():
    return render_template('index.html')

# 2. Login page
@app.route('/login', methods=['GET', 'POST'])
def login():

    if session.get('user_id'):
        return redirect(url_for('dashboard'))

    error = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        with open("User.json", "r") as f:
            data = json.load(f)

        for user in data["users"]:
            if username == user["username"] and password == user["password"]:
                session.clear()
                session["user"] = user["username"]
                session["user_id"] = user["user_id"]  # Added here

                return redirect(url_for("dashboard"))

        error = "Invalid username or password."

    return render_template('login.html', error=error)
import json
import os
from flask import Flask, render_template, request, redirect, url_for, session

#signup
@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # 1. Saare input fields nikalna
        username = request.form["username"]
        password = request.form["password"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        dob = request.form["dob"]

        # 2. data.json se purana data read karna
        file_path = 'User.json'
        users_data = {"users":[]}
        
        try:
            with open(file_path, 'r') as f:
                users_data = json.load(f)

        except FileNotFoundError:
             users_data = []

        except json.JSONDecodeError:
            users_data = [] # Agar file khali ya corrupt hai

        # 3. Check karna ki user pehle se exist karta hai ya nahi
        for user in users_data["users"]:
            if user.get('username') == username:
                return render_template('signup.html', error="Username already exists!")
            if user.get('email') == email:
                return render_template('signup.html', error="Email already registered!")
            existing_ids = [
                             int(user["user_id"][1:])
                             for user in users_data["users"]
                                if user.get("user_id", "").startswith("u")
                                        and user["user_id"][1:].isdigit()
                            ]


            new_id = f"u{max(existing_ids, default=0) + 1}"

        # 4. Naya user create karna (Dictionary format mein)
        new_user = {
            "user_id":new_id,
            "username": username,
            "password": password,  # Note: Real apps mein password ko hash karna chahiye!
            
        }

        # 5. Data ko list mein append karna
        users_data["users"].append(new_user)

        # 6. Wapas data.json file mein save karna (indent=4 se file readable banegi)
        with open(file_path, 'w') as f:
            json.dump(users_data, f, indent=4)
        with open("data.json", "r") as f:
            data = json.load(f)

            new_user_data = {
                "user_id": new_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "dob": dob,
                "daily_tasks": [],
                "goals": []
            }

            data["users"].append(new_user_data)

            with open("data.json", "w") as f:
                json.dump(data, f, indent=4)
        session['user_id']=new_id
        session["user"] = username
        # 7. Success ke baad login page par bhej dena
        return redirect(url_for('dashboard')) 

    return render_template("signup.html")

# 4. Dashboard
@app.route('/dashboard')
def dashboard():
    username = session.get('user')

    if not username:
        return redirect(url_for('login'))

    data = {
        'name': username,
        'role': 'Admin',
        'tasks': [
            'Practice Python',
            'Learn Flask',
            'Build a web page'
        ]
    }

    return render_template('dashboard.html', user=data)


# 5. Logout and return home
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

#Home page 
 
@app.route('/home')
def home():
    return render_template('home.html')

#Goal
@app.route('/goal', methods=["GET", "POST"])
def goal():
    userid = session.get('user_id')

    with open('data.json', 'r') as f:
        users_data = json.load(f)

    current_user = None
    for user in users_data["users"]:
        if user["user_id"] == userid:
            current_user = user
            break

    if current_user is None:
        return redirect(url_for('login'))

    if "goals" not in current_user:
        current_user["goals"] = []

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        if title:
            current_user["goals"].append({
                "title": title,
                "description": description
            })
            with open('data.json', 'w') as f:
                json.dump(users_data, f, indent=4)
        return redirect(url_for('goal'))

    return render_template('goal.html', goals=current_user["goals"])


@app.route('/goal/delete/<int:index>', methods=["POST"])
def delete_goal(index):
    userid = session.get('user_id')

    with open('data.json', 'r') as f:
        users_data = json.load(f)

    current_user = None
    for user in users_data["users"]:
        if user["user_id"] == userid:
            current_user = user
            break

    if current_user is None:
        return redirect(url_for('login'))

    goals = current_user.get("goals", [])
    if 0 <= index < len(goals):
        goals.pop(index)
        with open('data.json', 'w') as f:
            json.dump(users_data, f, indent=4)

    return redirect(url_for('goal'))
#task manage
@app.route('/task', methods=["GET", "POST"])
def task():
    userid = session.get('user_id')

    with open('data.json', 'r') as f:
        users_data = json.load(f)

    current_user = None
    for user in users_data["users"]:
        if user["user_id"] == userid:
            current_user = user
            break

    if current_user is None:
        return redirect(url_for('login'))

    if "daily_tasks" not in current_user:
        current_user["daily_tasks"] = []

    if request.method == "POST":
        task_name = request.form.get("task_name", "").strip()
        if task_name:
            current_user["daily_tasks"].append({
                "name": task_name,
                "done": False
            })
            with open('data.json', 'w') as f:
                json.dump(users_data, f, indent=4)
        return redirect(url_for('task'))

    return render_template('Daily task.html', daily_tasks=current_user["daily_tasks"])


@app.route('/task/toggle/<int:index>', methods=["POST"])
def toggle_task(index):
    userid = session.get('user_id')

    with open('data.json', 'r') as f:
        users_data = json.load(f)

    current_user = None
    for user in users_data["users"]:
        if user["user_id"] == userid:
            current_user = user
            break

    if current_user is None:
        return redirect(url_for('login'))

    tasks = current_user.get("daily_tasks", [])
    if 0 <= index < len(tasks):
        tasks[index]["done"] = not tasks[index]["done"]
        with open('data.json', 'w') as f:
            json.dump(users_data, f, indent=4)

    return redirect(url_for('task'))


@app.route('/task/delete/<int:index>', methods=["POST"])
def delete_task(index):
    userid = session.get('user_id')

    with open('data.json', 'r') as f:
        users_data = json.load(f)

    current_user = None
    for user in users_data["users"]:
        if user["user_id"] == userid:
            current_user = user
            break

    if current_user is None:
        return redirect(url_for('login'))

    tasks = current_user.get("daily_tasks", [])
    if 0 <= index < len(tasks):
        tasks.pop(index)
        with open('data.json', 'w') as f:
            json.dump(users_data, f, indent=4)

    return redirect(url_for('task'))


if __name__ == '__main__':
    app.run(debug=True)