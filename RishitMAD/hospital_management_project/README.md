# Hospital Management System (HMS)

A Flask-based web application for managing hospital operations, including patient, doctor, and appointment scheduling.

## Features

- **Role-Based Access Control:** Separate dashboards and functionalities for Admins, Doctors, and Patients.
- **Admin Panel:** Full CRUD control over doctors, patients, and departments. Includes a dashboard with appointment statistics.
- **Doctor Portal:** View upcoming appointments, manage availability for the next 7 days, update patient treatment history, and cancel appointments.
- **Patient Portal:** Register an account, search for doctors by name or specialization, book appointments based on real-time availability, view treatment history, and manage their profile.
- **RESTful API:** Provides API endpoints for managing doctors and viewing appointment statistics.
- **Secure Forms:** All forms are protected against CSRF attacks and include both backend and frontend validation.

## Tech Stack

- **Backend:** Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **Database:** SQLite (programmatically created)
- **Frontend:** HTML, CSS, Bootstrap 5, Jinja2, Chart.js
- **Environment:** Python, Venv

## Setup and Installation

### Prerequisites

- Python 3.8+
- `pip` and `venv`

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-folder>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the database and run migrations:**
    The application will create the `hospital.db` file and the admin user automatically upon the first run. If you change the models in `models/models.py`, you must generate a new migration.
    ```bash
    # First time, or if migrations folder is deleted
    flask db init

    # On model changes
    flask db migrate -m "Describe your change"
    flask db upgrade
    ```

5.  **Run the application:**
    ```bash
    flask run
    ```
    The application will be available at `http://127.0.0.1:5000`.

## Default Admin Credentials

- **Username:** `admin`
- **Password:** `admin_password`

*(These are set programmatically in `app.py` on the first run if the admin user does not exist)*

## API Usage Example

You can interact with the Doctor API using tools like `curl` or Postman.

**Example: Get all doctors**
```bash
curl -X GET http://127.0.0.1:5000/api/doctors```

**Example: Create a new doctor (requires admin login/session cookie)**
```bash
# This example is conceptual for curl as it requires authentication.
# It's easier to use a tool like Postman and log in as admin first.
curl -X POST http://127.0.0.1:5000/api/doctors \
-H "Content-Type: application/json" \
-d '{"name": "Dr. Strange", "username": "strange", "password": "password123", "specialization_id": 1}'
