from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'encryptionKey'

# JSON file paths - store in the same directory as app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, 'users.json')
TASKS_FILE = os.path.join(BASE_DIR, 'tasks.json')

# Helper functions for JSON operations
def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_tasks():
    """Load tasks from JSON file"""
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_tasks(tasks):
    """Save tasks to JSON file"""
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

def init_admin():
    """Initialize admin account if it doesn't exist"""
    users = load_users()
    if 'admin@admin.com' not in users:
        users['admin@admin.com'] = {
            'password': generate_password_hash('admin123'),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'role': 'admin',
            'is_admin': True
        }
        save_users(users)
        
        # Create empty task list for admin
        tasks = load_tasks()
        tasks['admin@admin.com'] = []
        save_tasks(tasks)

def email_exists(email):
    """Check if email already exists"""
    users = load_users()
    return email in users

def create_user(email, password):
    """Create a new user with hashed password using email as primary key"""
    users = load_users()
    if email in users:
        return False
    users[email] = {
        'password': generate_password_hash(password),
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'role': 'user',
        'is_admin': False
    }
    save_users(users)
    
    # Create empty task list for user
    tasks = load_tasks()
    tasks[email] = []
    save_tasks(tasks)
    return True

def verify_user(email, password):
    """Verify user credentials"""
    users = load_users()
    if email in users:
        return check_password_hash(users[email]['password'], password)
    return False

def is_admin(email):
    """Check if user is admin"""
    users = load_users()
    return users.get(email, {}).get('is_admin', False)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not email or not password or not confirm_password:
            flash('All fields are required!', 'error')
            return redirect(url_for('register'))
        
        # Basic email validation
        if '@' not in email or '.' not in email:
            flash('Please enter a valid email address!', 'error')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters!', 'error')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))
        
        if email_exists(email):
            flash('This email is already registered!', 'error')
            return redirect(url_for('register'))
        
        if create_user(email, password):
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registration failed!', 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if verify_user(email, password):
            session['user'] = email
            if is_admin(email):
                flash(f'Welcome Admin!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash(f'Welcome back, {email}!', 'success')
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if verify_user(email, password) and is_admin(email):
            session['user'] = email
            flash(f'Welcome back Admin!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials!', 'error')
            return redirect(url_for('admin_login'))
    
    return render_template('admin_login.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    user = session.get('user')
    if not user or not is_admin(user):
        return redirect(url_for('admin_login'))
    
    users = load_users()
    tasks = load_tasks()
    
    # Prepare user statistics
    user_stats = []
    for email, user_data in users.items():
        user_tasks = tasks.get(email, [])
        completed_count = len([t for t in user_tasks if t.get('completed', False)])
        user_stats.append({
            'email': email,
            'role': user_data.get('role', 'user'),
            'created_at': user_data.get('created_at', 'N/A'),
            'total_tasks': len(user_tasks),
            'completed_tasks': completed_count,
            'is_admin': user_data.get('is_admin', False)
        })
    
    return render_template('admin_dashboard.html', users=user_stats, admin=user)

@app.route('/admin/delete-user/<email>')
def admin_delete_user(email):
    current_user = session.get('user')
    if not current_user or not is_admin(current_user):
        return redirect(url_for('admin_login'))
    
    # Prevent admin from deleting themselves
    if email == current_user:
        flash('You cannot delete your own account!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    users = load_users()
    tasks = load_tasks()
    
    if email in users:
        del users[email]
        save_users(users)
        
        if email in tasks:
            del tasks[email]
            save_tasks(tasks)
        
        flash(f'User "{email}" deleted successfully!', 'success')
    else:
        flash('User not found!', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/dashboard')
def dashboard():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    
    # Prevent admin from using regular dashboard
    if is_admin(user):
        return redirect(url_for('admin_dashboard'))
    
    users = load_users()
    tasks = load_tasks()
    
    user_data = users.get(user, {})
    user_tasks = tasks.get(user, [])
    
    completed_count = len([t for t in user_tasks if t.get('completed', False)])
    total_count = len(user_tasks)
    
    data = {
        'name': user,
        'role': user_data.get('role', 'user'),
        'created_at': user_data.get('created_at', 'N/A'),
        'tasks': user_tasks,
        'completed': completed_count,
        'total': total_count
    }
    
    return render_template('dashboard.html', user=data)

@app.route('/add-task', methods=['POST'])
def add_task():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    
    task_name = request.form.get('task_name')
    if task_name:
        tasks = load_tasks()
        tasks[user].append({
            'id': len(tasks[user]) + 1,
            'name': task_name,
            'completed': False,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        save_tasks(tasks)
        flash('Task added successfully!', 'success')
    
    return redirect(url_for('dashboard'))

@app.route('/complete-task/<int:task_id>')
def complete_task(task_id):
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    
    tasks = load_tasks()
    for task in tasks[user]:
        if task['id'] == task_id:
            task['completed'] = not task['completed']
            break
    save_tasks(tasks)
    
    return redirect(url_for('dashboard'))

@app.route('/delete-task/<int:task_id>')
def delete_task(task_id):
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    
    tasks = load_tasks()
    tasks[user] = [t for t in tasks[user] if t['id'] != task_id]
    save_tasks(tasks)
    
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    # Initialize admin account on startup
    init_admin()
    app.run(debug=True)