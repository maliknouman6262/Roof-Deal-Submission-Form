# Roof Deal Submission Application

This project is a lightweight web form designed for sales representatives to submit new roof deals. The backend is based on the **Flask** framework, which saves form data and uploaded files to a **MySQL** database and sends automatic email notifications. The entire application is containerized using **Docker** to facilitate easy deployment in any environment.

## Technologies Used

* **Frontend:** HTML, CSS (Bootstrap), JavaScript
* **Backend:** Python, Flask, Flask-CORS, Werkzeug, MySQL-Connector
* **Database:** MySQL
* **Containerization:** Docker, Docker Compose

---

## Project Setup (Using Docker)

The easiest way to run the project is by using Docker and Docker Compose. With this method, you do not need to install Python, Flask, or MySQL separately on your system.

### Prerequisites

* **Docker:** Ensure that Docker is installed on your system. If not, you can download it from here: [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Steps

1.  **Project Files**
    The project includes the following files:
    * `app.py`: The Flask backend code.
    * `index.html`: The web form's frontend code.
    * `requirements.txt`: The list of Python dependencies.
    * `docker-compose.yml`: The file that defines the Docker services.
    * `Dockerfile`: The instructions for building the Flask application image.

2.  **Update Credentials in `docker-compose.yml`**
    Update your MySQL database and Gmail email details in the `docker-compose.yml` file.

    ```yaml
    services:
      web:
        environment:
          # ...
          - DB_USER=root
          - DB_PASSWORD=123@Malik
          - DB_DATABASE=roof_deals_db
          - EMAIL_USER=your-email@gmail.com
          - EMAIL_PASSWORD=your-app-password
    
      db:
        environment:
          - MYSQL_ROOT_PASSWORD=123@Malik #Use your owen database password please if you not comfortable using my database.
          - MYSQL_DATABASE=roof_deals_db
    ```

    > **Note:** For Gmail, you must use an "App Password" instead of your regular Gmail account password. This requires 2-Step Verification to be enabled.

3.  **Run the Application**
    Open the terminal in the project directory and run this command:
    ```sh
    docker compose up --build
    ```
    This command will build and run two containers: one for the web app and one for the MySQL database.

4.  **Access the Application**
    Once the containers are up and running, you can access the application at these URLs:
    * **Form:** `http://localhost:5000`
    * **Submitted Deals:** `http://localhost:5000/view-deals`

---

## File Structure
/roof-deal-system
├── app.py                  # Flask backend code
├── index.html              # Frontend web form
├── requirements.txt        # Python dependencies
├── Dockerfile              # Instructions for building the web app image
└── docker-compose.yml      # Service definitions for Docker

---

## Backend Endpoints

* `POST /submit-roof-deal`: Accepts form data and files, saves them to the database, and sends an email notification.
* `GET /view-deals`: Displays all deals from the database on an HTML page.
* `GET /get-deals`: Returns all deals from the database in JSON format.