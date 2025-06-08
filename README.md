# HireHub Developer Documentation

## Project Overview

HireHub is an Applicant Tracking System (ATS) designed to streamline the recruitment process. It helps manage job applicants, track their progress through various hiring stages, and facilitates collaboration among the hiring team.

### Key Features

*   **Applicant Management:** Create, view, and manage applicant profiles.
*   **Stage Tracking:** Track applicants through customizable hiring stages (e.g., Submitted, Under Review, Interview, Hired, Rejected).
*   **Resume Management:** Upload and store applicant resumes.
*   **Interview Scheduling & Feedback:** (Functionality to be detailed based on views and forms)
*   **Search & Filtering:** (Functionality to be detailed based on views and forms)
*   **Reporting & Analytics:** (Functionality to be detailed based on views and forms)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python (version 3.8 or higher recommended)
*   Django (version 3.x or 4.x - check \`requirements.txt\`)
*   pip (Python package installer)
*   Git

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/original-owner/hirehub.git # Replace with the actual repository URL
    cd hirehub
    ```
2.  **Create and activate a virtual environment:**
    *   On macOS and Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Apply database migrations:**
    The HireHub project uses SQLite by default for local development, which is configured in \`hirehub/hirehub_django/settings.py\`.
    ```bash
    python hirehub/manage.py migrate
    ```
5.  **Create a superuser (optional but recommended for accessing the admin panel):**
    ```bash
    python hirehub/manage.py createsuperuser
    ```
    Follow the prompts to create a username and password.

6.  **Run the development server:**
    ```bash
    python hirehub/manage.py runserver
    ```
    The application will be accessible at \`http://127.0.0.1:8000/\`. The admin panel can be accessed at \`http://127.0.0.1:8000/admin/\`.

## Project Structure

The project follows a standard Django project layout:

```
hirehub/
├── .github/                    # GitHub Actions workflows
├── ats/                        # The core Applicant Tracking System app
│   ├── migrations/             # Database migrations for the ats app
│   ├── static/ats/             # Static files (CSS, JS, images) for the ats app
│   │   ├── css/
│   │   └── js/
│   ├── templates/ats/          # HTML templates for the ats app
│   ├── __init__.py
│   ├── admin.py                # Django admin configurations for ats models
│   ├── apps.py                 # Application configuration for the ats app
│   ├── forms.py                # Django forms for the ats app
│   ├── models.py               # Database models for the ats app
│   ├── serializers.py          # Serializers for API views (if any)
│   ├── tests.py                # Unit tests for the ats app
│   ├── urls.py                 # URL routing for the ats app
│   └── views.py                # Views (request handlers) for the ats app
├── hirehub_django/             # Django project configuration
│   ├── __init__.py
│   ├── asgi.py                 # ASGI entry point for asynchronous servers
│   ├── settings.py             # Django project settings
│   ├── urls.py                 # Project-level URL routing
│   └── wsgi.py                 # WSGI entry point for synchronous servers
├── static/                     # Project-wide static files (collected by collectstatic)
├── templates/                  # Project-wide templates
├── manage.py                   # Django's command-line utility
├── README.md                   # This file
├── requirements.txt            # Python package dependencies
└── LICENSE                     # Project license information
└── .gitignore                  # Specifies intentionally untracked files that Git should ignore
```

### Key Components:

*   **`manage.py`**: A command-line utility that lets you interact with this Django project in various ways (e.g., running the development server, creating database migrations).
*   **`hirehub_django/settings.py`**: Contains all the project's configuration, such as database settings, installed apps, middleware, template paths, etc.
*   **`hirehub_django/urls.py`**: The main URL configuration for the project. It includes URL patterns from individual apps.
*   **`LICENSE`**: Contains the open-source license information for the project.
*   **`.gitignore`**: Specifies intentionally untracked files that Git should ignore (e.g., `__pycache__/`, `*.sqlite3`, `venv/`).
*   **`ats/`**: This is the primary application for HireHub.
    *   **`ats/models.py`**: Defines the database schema through Django models (e.g., `Applicant` model).
    *   **`ats/views.py`**: Contains the logic that handles requests and returns responses (e.g., rendering HTML templates with data).
    *   **`ats/urls.py`**: Defines the URL patterns specific to the `ats` application.
    *   **`ats/templates/ats/`**: Stores the HTML templates used to display data to the user.
    *   **`ats/static/ats/`**: Contains static assets like CSS and JavaScript files for the `ats` application.
    *   **`ats/forms.py`**: Defines forms used for data input and validation.
    *   **`ats/serializers.py`**: Contains serializers for converting complex data types, like queryset and model instances, to native Python datatypes that can then be easily rendered into JSON, XML or other content types (typically used for building APIs).

## Models

The primary model in the HireHub application is `Applicant`.

### `ats.models.Applicant`

This model stores all information related to a job applicant.

**Fields:**

*   **`name` (CharField):** The full name of the applicant.
*   **`email` (EmailField):** The applicant's email address.
*   **`phone` (CharField):** The applicant's phone number (optional).
*   **`current_stage` (CharField):** The current stage of the applicant in the hiring pipeline.
    *   Choices: 'Submitted', 'Under Review', 'Interview Stage', 'Technical Assessment', 'Final Interview', 'Offer Extended', 'Hired', 'Rejected'.
    *   Default: 'Submitted'.
*   **`source` (CharField):** How the applicant was sourced.
    *   Choices: 'LinkedIn', 'Indeed', 'Referral', 'Company Website', 'Job Board', 'Other'.
*   **`tags` (TextField):** Comma-separated tags for categorizing or adding keywords to an applicant (optional).
*   **`resume_file` (FileField):** The uploaded resume file for the applicant (optional). Stored in the `resumes/` directory.
*   **`resume_text` (TextField):** Extracted text content from the resume (optional).
*   **`interviewers` (TextField):** Names of the interviewers involved (optional).
*   **`interview_dates` (TextField):** Dates and times of scheduled interviews (optional).
*   **`comments_ta` (TextField):** Comments or feedback from the technical assessment stage (optional).
*   **`comments_initial_call` (TextField):** Comments or feedback from the initial call (optional).
*   **`comments_evaluation` (TextField):** General evaluation comments (optional).
*   **`overall_feedback` (TextField):** Overall feedback on the applicant (optional).
*   **`final_decision` (CharField):** The final hiring decision for the applicant (optional).
*   **`created_at` (DateTimeField):** Timestamp of when the applicant record was created (auto-generated).
*   **`updated_at` (DateTimeField):** Timestamp of the last update to the applicant record (auto-generated).
*   **`last_status_update` (DateTimeField):** Timestamp of the last status update (auto-generated, typically same as `updated_at`).

**Meta Options:**

*   `ordering = ['-created_at']`: Applicants are ordered by their creation date in descending order by default.

This model is central to the application's functionality, and understanding its structure is key to working with applicant data.

## Running Tests

The project includes a suite of tests to ensure code quality and functionality. Tests for the `ats` application are located in `hirehub/ats/tests.py`.

To run the tests:

1.  Ensure your virtual environment is activated and all dependencies are installed.
2.  Navigate to the directory containing `manage.py` (i.e., `hirehub/`).
3.  Run the following command:

    ```bash
    python manage.py test ats
    ```
    This command will discover and run all tests within the `ats` application.

    To run all tests in the project (if other apps with tests exist):
    ```bash
    python manage.py test
    ```

### Writing Tests

When adding new features or fixing bugs, it is highly encouraged to write new tests or update existing ones. This helps maintain code stability and prevents regressions.

*   Tests should be written using Django's testing framework.
*   Focus on testing individual units of code (unit tests) as well as integration points.
*   Ensure tests cover both success and failure scenarios.

## Contributing

Contributions are welcome and appreciated! To contribute to HireHub, please follow these guidelines:

1.  **Fork the Repository:** Start by forking the main HireHub repository to your own GitHub account.
2.  **Clone Your Fork:** Clone your forked repository to your local machine.
    ```bash
    git clone https://github.com/your-username/hirehub.git # Replace with your fork's URL
    cd hirehub
    ```
3.  **Create a New Branch:** Create a new branch for your feature or bug fix. Use a descriptive branch name (e.g., `feature/add-new-field` or `bugfix/fix-login-issue`).
    ```bash
    git checkout -b feature/your-feature-name
    ```
4.  **Make Your Changes:** Implement your feature or bug fix.
    *   Follow PEP 8 coding standards for Python.
    *   Write clear, concise, and well-documented code.
    *   Add or update tests as necessary.
5.  **Test Your Changes:** Ensure all tests pass.
    ```bash
    python manage.py test ats
    ```
6.  **Commit Your Changes:** Commit your changes with a clear and descriptive commit message.
    ```bash
    git add .
    git commit -m "feat: Implement X feature"
    ```
    Or for a bug fix:
    ```bash
    git commit -m "fix: Resolve Y bug in Z component"
    ```
7.  **Push to Your Fork:** Push your changes to your forked repository.
    ```bash
    git push origin feature/your-feature-name
    ```
8.  **Submit a Pull Request (PR):** Open a pull request from your branch to the `main` branch (or the appropriate target branch) of the original HireHub repository.
    *   Provide a clear title and description for your PR, explaining the changes you've made and why.
    *   Reference any relevant issue numbers.

### Code Style

*   **Python:** Adhere to PEP 8 guidelines. Consider using a linter like Flake8.
*   **Django:** Follow Django coding style and best practices.
*   **HTML/CSS/JS:** Maintain clean and readable code.

### Communication

*   If you plan to work on a major feature, it's a good idea to open an issue first to discuss your approach.
*   Be responsive to feedback on your pull requests.

By contributing to HireHub, you agree that your contributions will be licensed under the project's LICENSE.

## Deployment

This section outlines how the HireHub application can be deployed to a production environment.

(Details on the deployment process are specific to the chosen hosting provider and infrastructure. Common deployment strategies for Django applications include using platforms like Heroku, AWS Elastic Beanstalk, Google Cloud App Engine, or setting up a dedicated server with Gunicorn/uWSGI and Nginx.)

**General Steps for Production Deployment (Conceptual):**

1.  **Server Setup:** Provision a server (e.g., a Linux VM).
2.  **Database Configuration:** Set up a production-grade database (e.g., PostgreSQL, MySQL).
3.  **Environment Variables:** Configure environment variables for sensitive settings (e.g., `SECRET_KEY`, database credentials, `DEBUG=False`).
4.  **Static Files:** Run `python manage.py collectstatic` to gather all static files into a single directory.
5.  **WSGI Server:** Use a production WSGI server like Gunicorn or uWSGI to run the Django application.
6.  **Web Server (Reverse Proxy):** Use a web server like Nginx or Apache to serve static files and proxy requests to the WSGI server.
7.  **Security:**
    *   Ensure `DEBUG` is set to `False` in `settings.py`.
    *   Configure `ALLOWED_HOSTS` in `settings.py`.
    *   Set up HTTPS.
8.  **Process Management:** Use a process manager like `systemd` or `supervisor` to keep the WSGI server running.

**Note:** The GitHub Actions workflow in `.github/workflows/django-ci.yml` provides an example of a CI setup, which might include steps relevant to a deployment pipeline. Further details should be added here as the project's deployment strategy is finalized.
