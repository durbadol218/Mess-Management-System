# 🧾 Mess Management System

A full-stack web application to manage mess bills, user registrations, monthly reports, and admin operations — built using **Django**, **Django REST Framework**, and **JavaScript**.

## 🚀 Features

- 🔐 User registration and login (token-based authentication)
- 👥 Separate user roles: Member and Admin
- 🧮 Monthly bill tracking for each user
- 📊 Admin dashboard to view and manage all users’ bills
- 📅 Filter bills by year and month
- 📈 Real-time bill updates
- 📨 Email notifications (optional integration)

## 🛠️ Tech Stack

**Backend:**
- Python
- Django
- Django REST Framework

**Frontend:**
- HTML, CSS, Bootstrap
- JavaScript (Vanilla)
- Fetch API

**Database:**
- SQLite (dev) / PostgreSQL (production-ready)

## 📦 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/users/register/` | Register a new user |
| `POST` | `/users/login/` | Log in and get token |
| `GET`  | `/bills/history/?year=2025&month=6` | View monthly bills |
| `GET` | `/bills/summary/(?P<year>\d{4})/(?P<month>\d{1,2})/$` | Get bill summary for a specific month |
| `POST` | `/complaints/create/` | Submit a complaint to the admin panel |
| `GET` | `/complaints/user/` | View all complaints submitted by the current user |
| `GET` | `/complaints/admin/` | Admin can view all submitted complaints |

## 🧑‍💻 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/durbadol218/Mess-Management-System.git
cd mess-management-system
```
### 2. Create a virtual environment & install dependencies
```bash
python -m venv env
source env/bin/activate  # For Windows: env\Scripts\activate
pip install -r requirements.txt

```
### 3. Run migrations and start the server
```bash
python manage.py migrate
python manage.py runserver
```
### 4. Open in browser
Once the server is running, open your browser and visit: http://127.0.0.1:8000/
