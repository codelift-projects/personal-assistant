# Personal Assistant - Task Management Application

## Overview

Personal Assistant is a web-based task management application built with Flask where users can register, login, and manage their daily tasks. It includes a comprehensive admin panel for managing all users and monitoring system-wide statistics.

---

## Features

### 1. User Authentication
- **Registration** - Users register with email (unique identifier) and password
- **Login** - Email + password authentication with secure verification
- **Password Security** - Passwords are hashed using `werkzeug.security` (scrypt algorithm)
- **Session Management** - Secure session-based authentication

### 2. Task Management
- **Add Tasks** - Create new tasks with descriptions
- **Complete Tasks** - Mark tasks as done/pending
- **Delete Tasks** - Remove tasks from the list
- **Task Metadata** - Each task includes:
  - Unique ID
  - Name/description
  - Completion status
  - Creation timestamp

### 3. User Dashboard
- View all personal tasks with completion status
- Real-time task statistics:
  - Total tasks count
  - Completed tasks count
  - Pending tasks count
- Progress tracking with visual progress bars
- Quick actions to manage tasks

### 4. Admin Dashboard
- **View all registered users** with their email addresses
- **User Statistics** - See each user's task metrics
- **Task Completion Rates** - Monitor individual and system-wide progress
- **User Management** - Delete users and their tasks (except admin account)
- **System Analytics** - Total users, total tasks, completion rate

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              Frontend (HTML/CSS)                    │
│  ┌──────────────┬──────────────┬──────────────┐    │
│  │ Home Page    │ User Portal  │ Admin Portal │    │
│  ├─ Register   ├─ Dashboard  ├─ User List   │    │
│  ├─ Login      └─ Tasks      └─ Analytics   │    │
│  └──────────────┴──────────────┴──────────────┘    │
└─────────────────────────────────────────────────────┘
                      ↕ HTTP Requests
┌─────────────────────────────────────────────────────┐
│              Backend (Flask - app.py)               │
│  ┌──────────────────────────────────────────────┐  │
│  │ Routes:                                      │  │
│  │ - /register      - /login      - /logout     │  │
│  │ - /dashboard     - /add-task   - /delete-task│  │
│  │ - /admin-login   - /admin-dashboard          │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                      ↕ JSON Read/Write
┌─────────────────────────────────────────────────────┐
│         Data Storage (JSON Files)                   │
│  ├─ users.json  (user accounts)                    │
│  └─ tasks.json  (user tasks)                       │
└─────────────────────────────────────────────────────┘
```

---

## Technologies Used

| Component | Technology |
|-----------|-----------|
| **Backend** | Flask (Python 3.12) |
| **Frontend** | HTML5 + CSS3 |
| **Database** | JSON files (local storage) |
| **Authentication** | werkzeug.security (scrypt hashing) |
| **Session Management** | Flask Sessions |

---

## Project Structure

```
personal-assistant/
├── app.py                          # Main Flask application
├── users.json                      # User accounts data storage
├── tasks.json                      # User tasks data storage
├── README.md                       # Project documentation
└── templates/
    ├── home.html                   # Landing page with features
    ├── register.html               # User registration form
    ├── login.html                  # User login form
    ├── dashboard.html              # User task dashboard
    ├── admin_login.html            # Admin portal login
    └── admin_dashboard.html        # Admin management panel
```

---

## Routes & Endpoints

| Route | Method | Purpose | Auth Required |
|-------|--------|---------|---------------|
| `/` | GET | Home/Landing page | No |
| `/register` | GET, POST | User registration | No |
| `/login` | GET, POST | User login | No |
| `/dashboard` | GET | User task dashboard | Yes (User) |
| `/add-task` | POST | Add new task | Yes (User) |
| `/complete-task/<id>` | GET | Toggle task completion | Yes (User) |
| `/delete-task/<id>` | GET | Delete a task | Yes (User) |
| `/admin-login` | GET, POST | Admin portal login | No |
| `/admin-dashboard` | GET | Admin management panel | Yes (Admin) |
| `/admin/delete-user/<email>` | GET | Delete user account | Yes (Admin) |
| `/logout` | GET | Logout user | Yes (Any) |

---

## Data Storage

### users.json
Stores user account information:
```json
{
  "user@email.com": {
    "password": "scrypt:32768:8:1$...",
    "created_at": "2026-09-28 13:56:14",
    "role": "user",
    "is_admin": false
  },
  "admin@admin.com": {
    "password": "scrypt:32768:8:1$...",
    "created_at": "2026-09-28 13:50:46",
    "role": "admin",
    "is_admin": true
  }
}
```

### tasks.json
Stores tasks organized by user email:
```json
{
  "user@email.com": [
    {
      "id": 1,
      "name": "Task description",
      "completed": false,
      "created_at": "2026-09-28 14:00:00"
    }
  ]
}
```

---

## Security Features

✅ **Email as Primary Key** - Unique identifier, prevents duplicate accounts  
✅ **Password Hashing** - Uses scrypt algorithm (one-way encryption)  
✅ **Session-Based Auth** - Secure session management  
✅ **Admin Protection** - Admin routes verify admin status  
✅ **Self-Delete Prevention** - Admins cannot delete their own account  
✅ **Email Validation** - Basic email format validation on registration  

---

## Installation & Setup

### Prerequisites
- Python 3.12+
- pip (Python package manager)
- Virtual environment (venv)

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/codelift-projects/personal-assistant.git
cd personal-assistant
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

3. **Install dependencies**
```bash
pip install flask werkzeug
```

4. **Run the application**
```bash
python app.py
```

5. **Access the application**
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## Default Admin Credentials

When the application starts, an admin account is automatically created:

- **Email:** `admin@admin.com`
- **Password:** `admin123`

⚠️ **Important:** Change the admin password immediately in production!

---

## Usage Guide

### For Users

1. **Registration**
   - Click "Register" on the home page
   - Enter your email address
   - Create a strong password (min 6 characters)
   - Confirm password and submit

2. **Login**
   - Click "Login" and enter your credentials
   - You'll be directed to your dashboard

3. **Managing Tasks**
   - Add tasks using the input field
   - Check the checkbox or click "Mark Done" to complete tasks
   - Click "Delete" to remove tasks
   - View progress in statistics cards

4. **Logout**
   - Click "Logout" to end your session

### For Admins

1. **Admin Login**
   - Click "Admin" button on home page
   - Enter admin email and password
   - Access the admin dashboard

2. **Monitor System**
   - View all registered users
   - See each user's task statistics
   - Track overall system metrics

3. **User Management**
   - Delete user accounts (this also removes all their tasks)
   - Cannot delete your own admin account

---

## Key Functions

### Authentication Functions
- `email_exists(email)` - Check if email is already registered
- `create_user(email, password)` - Register new user with hashed password
- `verify_user(email, password)` - Authenticate user credentials
- `is_admin(email)` - Check if user has admin privileges

### Task Functions
- `load_tasks()` - Load all tasks from JSON
- `save_tasks(tasks)` - Save tasks to JSON
- Routes handle: add, complete, and delete operations

### Admin Functions
- `init_admin()` - Initialize default admin account
- Admin dashboard displays user statistics
- Delete user functionality with safety checks

---

## Database Format

### Password Storage
Passwords are never stored in plain text. They are hashed using werkzeug's `generate_password_hash()`:
```python
hashed_password = generate_password_hash('user_password')
```

Verification uses `check_password_hash()`:
```python
is_valid = check_password_hash(stored_hash, entered_password)
```

---

## Future Enhancements

- [ ] Session timeout (auto-logout after inactivity)
- [ ] Password reset functionality
- [ ] Email verification for registration
- [ ] Task categories/tags
- [ ] Task due dates and reminders
- [ ] User profile management
- [ ] Export tasks to PDF/CSV
- [ ] Database migration (from JSON to SQL)
- [ ] Two-factor authentication (2FA)
- [ ] API endpoints for mobile apps

---

## Troubleshooting

### Issue: ModuleNotFoundError for flask
**Solution:** Install Flask with `pip install flask`

### Issue: Port 5000 already in use
**Solution:** Modify `app.run()` to use different port:
```python
app.run(debug=True, port=5001)
```

### Issue: JSON files not created
**Solution:** They auto-create on first registration. Or manually create empty files:
```bash
echo "{}" > users.json
echo "{}" > tasks.json
```

---

## License

This project is open source and available for educational and commercial use.

---

## Author

Created with ❤️ by Sunny Rarora  
Email: sunnyrarora@yahoo.com

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-09-28 | Initial release with email auth, tasks, and admin panel |

---

## Support

For issues, questions, or suggestions, please open an issue on GitHub or contact the author.
