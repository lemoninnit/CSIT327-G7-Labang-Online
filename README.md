# Labang Online

The primary purpose of LabangOnline is to modernize and digitize the delivery of barangay-level services in Barangay Labangon, Cebu City. At present, residents face long queues, delays, and limited transparency due to the barangay’s reliance on manual, paper-based processes. By creating a localized digital platform, this project directly addresses these inefficiencies and ensures that essential services such as certificate requests, complaint filing, and service inquiries are accessible anytime and anywhere.

## Features

- Registration form (name, DOB, address, contact)
- Barangay Labangon verification
- Email/phone verification
- Password setup & encryption
- Error handling & input validation
- Welcome message / confirmation email

## Installation

1. Clone the repository
2. Create virtual environment: `python -m venv env`
3. Activate environment: `source env/bin/activate` (Linux/Mac) or `env\Scripts\activate`
(Windows)
4. Install requirements: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Create superuser: `python manage.py createsuperuser`
7. Run server: `python manage.py runserver`

## Technology Stack
- Django
- SQLite (can be configured for other databases)
- HTML/CSS/JavaScript
