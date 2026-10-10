from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from pathlib import Path
import json

app = Flask(__name__)
app.secret_key = 'encryptionKey'

BASE = Path(__file__).parent
DB_FILE = BASE / "db.json"
USERDATA_FILE = BASE / "userdata.json"

global users
@app.route('/')
def home():
    with open(DB_FILE, "r") as f:
        db = json.load(f)
    with open(USERDATA_FILE, "r") as g:
        userdata = json.load(g)
    return render_template('home.html')

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
                
                # session['Achivements'] = u.get("name", u["Achivements"])
                for d in userdata["users"]:
                    if u["id"] == d['id']:
                        session['Achivements'] = d.get("name", d["Achivements"])
                        session['userdata'] = userdata
                        session['projects'] =  d["projects"]
                        
                
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

        for u in db["users"]:
            if u["username"].lower() == username.lower():
                flash("Username already taken")
                return redirect(url_for('signup'))

        new_user = {
            "id": "u_" + str(len(db["users"]) + 1).zfill(3),
            "name": name,
            "email": email,
            "username": username,
            "password": password
        }
        db["users"].append(new_user)

        with open(DB_FILE, "w") as f:
            json.dump(db, f, indent=2)

        flash("Account created. Please login.")
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/dashboard')
def dashboard():
    if not session.get('user'):
        return redirect(url_for('login'))

    data = {
        'name': session.get('name', session.get('user')),
        'achivement': session.get('achivement', session.get('user'))
        
    }
    return render_template('dashboard.html', user=data)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)