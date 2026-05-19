# Online Movie Streaming Platform - Amanix

## Overview

Amanix is an online movie streaming platform built using Django and connected to a MySQL database managed by PHPMyAdmin. The platform allows users to stream movies, manage accounts, and interact with the content dynamically.

## Features

- User Authentication (Login/Register)
- Movie Listings and Categories
- Movie Streaming Functionality
- Admin Panel for Content Management
- Secure and Optimized Performance

## Technologies Used

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: MySQL (Managed via PHPMyAdmin)
- **Server**: Apache

## Prerequisites

Ensure you have the following installed:

- Python 3.x
- Django
- MySQL
- PHP & PHPMyAdmin
- Apache Server (XAMPP recommended)

## How to Run the Online Movies Streaming Platform Project Using Python with Django and MySQL

### 1. Install Required Software

- Install Python: [Download Python](https://www.python.org/downloads/)
- Install XAMPP: [Download XAMPP](https://www.apachefriends.org/index.html)
- Install MySQL (if not included in XAMPP)

### 2. Open PHPMyAdmin

Go to: [http://localhost/phpmyadmin](http://localhost/phpmyadmin)

### 3. Create a Database

- Create a new database with the name **'amanix'**.

### 4. Import Database

- Import the `amanix.sql` file from the `database/` folder.


### 5. Set Up a Virtual Environment

```bash
python -m venv myvnev
cd myvnev
./Scripts/activate  # For Windows
source bin/activate  # For Linux/Mac
cd ..
```

### 6. Install Required Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install mysqlclient
```

### 7. Configure Django Database Settings

Update `settings.py` with MySQL credentials:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'amanix',
        'USER': 'root',  # Change if different
        'PASSWORD': '',  # Set your MySQL password
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 8. Apply Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 9. Create a Superuser (Admin)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 10. Run the Django Development Server

```bash
python manage.py runserver
```

### 11. Open the Website

Click **Ctrl + Left Click** on [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Admin Credentials

- **Username**: admin@123
- **Password**: admin@123

## Member Credentials

- **Username**: maulik@gmail.com
- **Password**: 123

Or, register a new user.

## Running the Project with XAMPP

1. Start Apache and MySQL from XAMPP Control Panel.
2. Ensure your MySQL database is correctly set up.
3. Run `python manage.py runserver` to start the Django application.

## Admin Panel

- Access: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- Login with the superuser credentials created earlier.

## Troubleshooting

- If MySQL is not connecting, verify the database name, user, and password in `settings.py`.
- Ensure MySQL service is running in XAMPP.
- Install MySQL dependencies if missing:

```bash
pip install mysqlclient
```

