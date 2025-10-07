## Labang Online

The primary purpose of Labang Online is to digitize barangay-level services in Barangay Labangon, Cebu City. This project targets long queues and paper-based processes by enabling online access to services like certificate requests, complaints, and inquiries.

## Sprint 1 Scope

- Registration form (name, DOB, address, contact)
- Barangay Labangon verification
- Email/phone verification (OTP)
- Password setup & encryption
- Error handling & input validation
- Welcome message / confirmation email


## Sprint 2 Scope

- Login form       
- Barangay Labangon verification
- Authentication backend
- Session management
- Password reset
- Error messages for failed login

- Resident ID photo upload
- Edit/update resident profile information
- View complete resident profile (including ID photo & dependents)

- Define entities and relationships (ERD creation)



## Quickstart (Windows, using Python launcher)

1) Ensure Python 3.13+ is installed. Verify: `py -V`
2) Option A: Virtual environment (recommended)

```
py -m venv .venv
# If activation scripts are missing, you can skip activation and use `py -m pip --user` below.
```

3) Install dependencies

```
py -m pip install --user django django-environ phonenumbers
```

4) Initialize database and run server

```
py manage.py migrate
py manage.py runserver
```

Open `http://127.0.0.1:8000/accounts/register/` to register and verify.

## Supabase (Session Pooler) setup

1) Install packages:
```
py -m pip install --user psycopg2-binary dj-database-url python-dotenv
```

2) In the Supabase dashboard → Project → Connect → Connection Info, copy the Session Pooler URL. It looks like:
```
postgresql://postgres:YOUR_PASSWORD@aws-0-<project-ref>.pooler.supabase.com:5432/postgres
```
Append `?sslmode=require`.

3) Create a `.env` in the project root:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@aws-0-<project-ref>.pooler.supabase.com:5432/postgres?sslmode=require
```

4) Migrate and run to verify the connection:
```
py manage.py migrate
py manage.py runserver
```

## Tech Stack
- Django
- Supabase
- HTML/CSS/JavaScript
