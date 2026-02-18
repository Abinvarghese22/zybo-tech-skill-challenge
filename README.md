# 💬 Real-Time Individual Chat Application

A real-time private messaging application built with **Django**, **Django Channels**, and **WebSocket** technology. Features include user authentication, online status tracking, read receipts, typing indicators, and message deletion.

## 🚀 Tech Stack

- **Python** 3.10+
- **Django** 4.2 (MVT Architecture)
- **Django Channels** 4.x (WebSocket)
- **SQLite** (Database)
- **HTML, CSS, JavaScript** (Frontend)
- **Bootstrap 5** (UI Framework)
- **Daphne** (ASGI Server)

## ✨ Features

### Core Features
- ✅ **User Authentication** – Register, Login, Logout
- ✅ **Custom User Model** – Email-based authentication with online status
- ✅ **Real-Time Messaging** – WebSocket-based private chat
- ✅ **Message History** – Persistent message storage in SQLite
- ✅ **Online/Offline Status** – Green dot indicator for online users
- ✅ **Read Receipts** – ✓ for sent, ✓✓ for read
- ✅ **Auto-Scroll** – Automatically scrolls to the latest message

### Bonus Features
- ✅ **Typing Indicator** – Shows when the other user is typing
- ✅ **Unread Message Count** – Badge showing unread messages per user
- ✅ **Delete Message** – Remove your own messages in real-time

### Additional Features
- 🔒 Secure WebSocket connections (authenticated users only)
- 📱 Fully responsive design
- 🎨 Modern glassmorphism UI with dark theme
- 🔍 User search functionality
- ♻️ Auto-reconnect on WebSocket disconnection

## 📁 Project Structure

```
chatapp/
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3
├── chatapp/                  # Main Django project
│   ├── __init__.py
│   ├── settings.py           # Project settings (ASGI, Channels, Auth)
│   ├── urls.py               # Root URL configuration
│   ├── asgi.py               # ASGI config with WebSocket routing
│   └── wsgi.py               # WSGI config
├── accounts/                 # Authentication app
│   ├── __init__.py
│   ├── models.py             # CustomUser model
│   ├── views.py              # Login, Register, Logout views
│   ├── forms.py              # Registration & Login forms
│   ├── urls.py               # Auth URL routes
│   ├── admin.py              # Admin configuration
│   └── apps.py
├── chat/                     # Chat app
│   ├── __init__.py
│   ├── models.py             # Message model
│   ├── views.py              # User list & Chat room views
│   ├── consumers.py          # WebSocket consumer
│   ├── routing.py            # WebSocket URL routing
│   ├── urls.py               # Chat URL routes
│   ├── admin.py              # Admin configuration
│   └── apps.py
├── templates/                # Django templates
│   ├── base.html             # Base template with navbar
│   ├── accounts/
│   │   ├── register.html     # Registration page
│   │   └── login.html        # Login page
│   └── chat/
│       ├── user_list.html    # User listing page
│       └── chat.html         # Chat room page
└── static/
    └── css/
        └── styles.css        # Custom styles
```

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd chatapp
   ```

2. **Create and activate a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py makemigrations accounts
   python manage.py makemigrations chat
   python manage.py migrate
   ```

5. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Open the app**
   - Visit: [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - Register two accounts in different browsers/tabs
   - Start chatting!

## 🔐 Test Credentials

| User | Email | Password |
|------|-------|----------|
| User 1 | user1@test.com | TestPass123! |
| User 2 | user2@test.com | TestPass123! |

> ⚠️ Create these accounts via the registration page after running migrations.

## 📱 Pages

| Page | URL | Description |
|------|-----|-------------|
| Register | `/accounts/register/` | Create a new account |
| Login | `/accounts/login/` | Sign in with email & password |
| User List | `/chat/` | View all users & start conversations |
| Chat Room | `/chat/<user_id>/` | Private chat with a specific user |

## 🏗️ Architecture

This project strictly follows Django's **MVT (Model-View-Template)** architecture:

- **Models** (`models.py`) – Define database schema (CustomUser, Message)
- **Views** (`views.py`) – Handle HTTP requests and context passing
- **Templates** (`templates/`) – Render UI using Django template engine
- **Consumers** (`consumers.py`) – Handle WebSocket communication logic

> ⚠️ Business logic is NOT written inside templates.

## 📜 License

This project is developed as a task submission for Zybo Tech Lab.
