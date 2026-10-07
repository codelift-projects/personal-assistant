from flask import Flask, render_template, request, redirect, url_for, session
import secrets
import json
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)


# 1. Home page
@app.route('/')
def home():
    return render_template('home.html')


# 2. Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user'):
        return redirect(url_for('dashboard'))

    error = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        withopen(user.json,"r")
        
            return redirect(url_for('dashboard'))

        error = 'Invalid username or password.'

    return render_template('login.html', error=error)
# # 3.signup
@app.route('/signup',methods=["GET","POST"])
def signup():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]
        dob=request.form["dob"]
        print("Username :",username)
        print("Password :",password)
        print("DOB :",dob)
        return
    render_template("signup.html")

# with open ("User.json","r") as f:
#     user =json.load(f) 
# with open ("User.json","w") as f:
#     json.dump(user,f)    

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
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)