from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user'] = request.form['username']
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    data = {'name': user, 'role': 'admin', 'tasks': ['task1', 'task2']}
    return render_template('dashboard.html', user=data)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)