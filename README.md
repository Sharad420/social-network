# Social Network Web App

A full-stack social networking application built with **Django** and **React**, supporting:

- User registration and login
- Following/unfollowing users
- Creating, editing, deleting, and liking posts
- Commenting on posts
- Real-time likes and comments with React interactivity
- Pagination and profile view with follow statistics

---

## 🚀 Features

- 🧾 **Authentication**: Register, login, logout (Django's built-in system)
- 📝 **Posting**: Create and edit posts dynamically
- 💬 **Comments**: View/add comments in real-time
- ❤️ **Likes**: Toggle likes with instant frontend update
- 👥 **Follow System**: Follow/unfollow users with follower stats
- 🧑‍💻 **Profile Pages**: View user profiles with their posts
- 🔁 **Pagination**: Server-side pagination of posts
- 🔐 **CSRF Protection**: All interactions secured via CSRF tokens
- 🎨 **Responsive UI**: Clean UI built with Bootstrap 5

---

## 🛠️ Tech Stack

- **Backend**: Django, Django REST Framework
- **Frontend**: React (via Babel), Bootstrap 5
- **Database**: SQLite (dev), ready for PostgreSQL in prod

---

## 📦 Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/social-network.git
   cd social-network

2. **Create and activate a virtual environment:**

    ```
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies:**
    ```pip install -r requirements.txt```

4.	**Apply migrations and start the server:**

    ```
    python manage.py migrate
    python manage.py runserver
    ```


License

This project is licensed under the MIT License — feel free to fork, use, and build upon it.