# 🏠 SharedBudget 

A full-stack web application designed to help roommates seamlessly track, split, and manage shared household expenses. Built with a focus on clean architecture, secure session management, and robust deployment practices.

## ✨ Features

* **Secure Authentication:** User registration and login system with password hashing (Werkzeug) and secure session cookies.
* **Household Management:** Create a new household or join an existing one using a unique generated Join Code.
* **Expense Tracking (CRUD):** Add, view, edit (via intuitive inline forms), and delete shared expenses.
* **Smart Localization (AI/LLM):** Integrates an LLM API to automatically translate and localize usernames into Hebrew for a native UI experience.
* **Defensive Programming:** Strict server-side validation and authorization checks to prevent Broken Object Level Authorization (BOLA) vulnerabilities (users can only edit/delete their own household's expenses).

## 🛠️ Tech Stack

* **Backend:** Python 3.11, Flask
* **Database:** SQLite (Development) / PostgreSQL-ready (Production), SQLAlchemy (ORM), Flask-Migrate
* **Frontend:** HTML5, CSS3, Vanilla JavaScript, Jinja2 Templating
* **DevOps & Architecture:** Docker, Gunicorn (WSGI), MVC Pattern, PRG (Post-Redirect-Get) Pattern

## 🚀 Getting Started (Run Locally with Docker)

The easiest way to run this application is using Docker. This ensures you have the exact environment and dependencies required.

### Prerequisites
* Docker Desktop installed on your machine.

### Installation & Running

1. **Clone the repository:**
    git clone [https://github.com/YOUR_USERNAME/SharedBudget.git](https://github.com/YOUR_USERNAME/SharedBudget.git)
    cd SharedBudget

2. **Build the Docker Image:**
    docker build -t shared-budget .

3. **Run the Container (with data persistence):**
    This command maps the local `instance` directory to the container, ensuring your database is not lost when the container stops.
    
    On Mac/Linux:
    docker run -p 5000:5000 -v $(pwd)/instance:/app/instance shared-budget
   
    On Windows (PowerShell):
    docker run -p 5000:5000 -v ${PWD}/instance:/app/instance shared-budget

4. **Access the App:**
    Open your browser and navigate to http://localhost:5000

## 🗺️ Roadmap (Future Features)
* **Admin Mode:** Designate a household manager with exclusive rights to remove users or delete the household.
* **Leave Household:** Allow users to safely detach from a household and migrate to a new one.
* **Monthly Reports:** Export expense breakdowns to CSV/PDF.

---
*Developed by Tal Kramer - www.linkedin.com/in/tal-kramer100

