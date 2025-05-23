# Quiz Master V1 - MAD I (Jan 2025)

## Author:
- Name: [Your Name]
- Roll No: [Your Roll No]
- Email ID: [Your Email]
- Description: A multi-user web application for exam preparation that provides quizzes across multiple subjects, allowing users to register, take quizzes, track their performance, and manage quiz content and user data.

## Project Overview
Quiz Master V1 is a platform for exam preparation. It allows users to register, attempt quizzes, and track their performance. Admins have the ability to manage quiz content, user data, and monitor user activity. This platform is developed using Flask for the backend, Flask-SQLAlchemy for database management, and various other technologies for frontend and functionality.

## Technologies Used:
- **Flask**: A lightweight WSGI web application framework.
- **Flask-SQLAlchemy**: SQL toolkit and ORM for Flask.
- **Flask-Login**: Manages user sessions and login/logout.
- **SQLite**: A lightweight, disk-based database for local storage.
- **Werkzeug Security**: Provides utilities for password hashing and verification.
- **HTML, CSS, Bootstrap**: For the frontend and structure.
- **Matplotlib**: For displaying summary graphs.

## DB Schema Design

### 1. User Table
- **id (Primary Key)**: Unique identifier for each user.
- **u_email (String, Unique)**: User's email.
- **u_username (String, Unique)**: User's unique username.
- **u_pw (String, Not Null)**: User's hashed password.
- **u_is_admin (Boolean, Default: False)**: Indicates if the user is an admin.
- **u_name (String, Not Null)**: User's full name.
- **is_blocked (Boolean, Default: False)**: Indicates if the user is blocked.

### 2. Subject Table
- **id (Primary Key)**: Unique identifier for each subject.
- **name (String, Not Null)**: Subject name.
- **desc (String, Nullable)**: Subject description.

### 3. Chapter Table
- **id (Primary Key)**: Unique identifier for each chapter.
- **name (String, Not Null)**: Chapter name.
- **desc (String, Nullable)**: Chapter description.
- **subject (Foreign Key → Subject.id, Not Null)**: Associated subject.

### 4. Quiz Table
- **id (Primary Key)**: Unique identifier for each quiz.
- **name (String, Not Null)**: Quiz name.
- **desc (String, Nullable)**: Quiz description.
- **chapter (Foreign Key → Chapter.id, Not Null)**: Associated chapter.
- **timer (Integer, Nullable)**: Time limit for the quiz (in minutes).
- **time (Time, Nullable)**: Quiz start time.
- **date (Date, Not Null)**: Quiz scheduled date.
- **remarks (String, Nullable)**: Additional remarks for the quiz.

### 5. Question Table
- **id (Primary Key)**: Unique identifier for each question.
- **question (String, Not Null)**: The quiz question.
- **option1 (String, Not Null)**: First answer option.
- **option2 (String, Not Null)**: Second answer option.
- **option3 (String, Not Null)**: Third answer option.
- **option4 (String, Not Null)**: Fourth answer option.
- **correct (Integer, Not Null)**: Correct answer (1-4 representing the correct option).
- **marks (Integer, Not Null)**: Marks assigned to the question.
- **quiz (Foreign Key → Quiz.id, Not Null)**: Associated quiz.

### 6. Score Table
- **id (Primary Key)**: Unique identifier for each score record.
- **user (Foreign Key → User.id, Not Null)**: User who attempted the quiz.
- **quiz (Foreign Key → Quiz.id, Not Null)**: Associated quiz.
- **last_score (Integer, Default: 0)**: Score of the last attempt.
- **total_score (Integer, Default: 0)**: Cumulative total score.
- **last_submit (JSON, Nullable)**: JSON data storing the last submission details.
- **time_taken (Integer, Nullable)**: Time taken to complete the quiz (in seconds).

## ER Diagram
[Insert ER diagram here]

## Architecture and Features:
- **Controllers**: The primary logic of the application, including routes and request handling, is defined in `app.py`.
- **Templates**: HTML files located in the `templates` directory for rendering views.
- **Models**: Defined in `app.py` to represent the database schema.

## Running the Application:
To run the app locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone [repository_url]
   cd [project_directory]

