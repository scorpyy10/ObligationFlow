# ObligationFlow Django Project

## Overview

ObligationFlow is a Django-based web application designed to manage and analyze documents, extract obligations, and track risk. It utilizes Celery for background task processing for extracting term clause and obligations and Redis as the message broker.

## Requirements

- Python 3.11.4
- Django 5.1.2
- Redis
- LibreOffice (for document conversion on non-Windows platforms)

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ObligationFlowDjango-main
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the environment:**
   - Ensure that Redis server is running on the port 6380.
   - Update any necessary settings in `ObligationFlowProject/settings.py`.

5. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Run Celery worker:**
   ```bash
   celery -A ObligationFlowProject worker --loglevel=info
   ```

7. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

8. **Access the application:**
   - Open your browser and navigate to `http://127.0.0.1:8000/` to start using the application.

## Features

- Document management with uploading and version control.
- Automated extraction of obligations and risk assessment.
- Scheduled background tasks using Celery.
- Compatibility across different platforms for document conversion.

## Additional Information

- Update the `celery.py` configuration as needed for different environments.
- The application assumes default configurations for simplicity; modify `settings.py` for production deployments.

## License

This project is licensed under the MIT License.

