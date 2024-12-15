# Car Service Management API

## Overview

This is a comprehensive RESTful API for managing car service appointments, built with FastAPI, SQLAlchemy, and Python. The API provides functionality for users, mechanics, services, cars, and appointments.

## Features

### User Management
- User registration and authentication
- Profile management
- Role-based access control (admin/customer)

### Car Management
- Add, update, and delete car information
- Associate cars with user accounts

### Service Management
- CRUD operations for services
- Admin-only service creation and modification

### Mechanic Management
- Mechanic registration and authentication
- Role-based access control (admin/mechanic)
- Appointment assignment

### Appointment System
- Create, update, and cancel service appointments
- Assign mechanics to appointments
- Email confirmation for appointments
- Status tracking (pending, confirmed, completed, canceled)

## Technology Stack

- **Language**: Python 3.9+
- **Web Framework**: FastAPI
- **ORM**: SQLAlchemy (Async)
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: bcrypt
- **Email**: FastAPI-Mail
- **Database**: Async SQLAlchemy (compatible with MySQL)


## Installation

1. Clone the repository:
```bash
git clone https://github.com/AntonKorinchuk/STO_management_API.git
cd STO_management_API
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Rename .env.template to .env file and populate it with the required data:
```
DB_USER=db_user
DB_PASSWORD=your_db_password
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=db_name

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

MAIL_USERNAME="your_email@gmail.com"
MAIL_PASSWORD="your_password"
MAIL_FROM="your_email@gmail.com"
```
5. Initialize the database(:
```bash
alembic upgrade head
```

## Running the Application

```bash
uvicorn main:app --reload
```

## API Endpoints

### Authentication
- `POST /users/register`: Register a new user
- `POST /users/login`: User login
- `POST /mechanics/register`: Register a new mechanic
- `POST /mechanics/login`: Mechanic login

### Users
- `GET /users/me`: Get current user profile
- `GET /users/`: List user's (Admin only)
- `PUT /users/{user_id}`: Update user profile
- `DELETE /users/{user_id}`: Delete user account

### Cars
- `POST /cars/`: Add a new car
- `GET /cars/`: List user's cars
- `PUT /cars/{car_id}`: Update car information
- `DELETE /cars/{car_id}`: Delete a car

### Services
- `POST /services/`: Create a service (admin only)
- `GET /services/`: List all services
- `PUT /services/{service_id}`: Update service
- `DELETE /services/{service_id}`: Delete service
- `GET /services/search`: Searches for services by name and/or price range

### Appointments
- `POST /appointments/`: Create a new appointment
- `GET /appointments/`: List user's appointments
- `PUT /appointments/{appointment_id}`: Update appointment
- `DELETE /appointments/{appointment_id}`: Cancel appointment
- `PUT /appointments/{appointment_id}/assign-mechanic`: Assign mechanic (admin only)

### Documents
- `POST /documents/upload`: Uploads a document for the current mechanic
- `GET /documents/`: List all documents for the current mechanic
- `GET /documents/all`: Fetches all documents (only admin)
- `PUT /documents/{document_id}` Updates a document's file and type
- `DELETE /documents/{document_id}` Deletes a document

### Mechanics
- `GET /mechanics/me`: Get current mechanic profile
- `GET /mechanics/`: List all mechanics (Admin only)
- `PUT /mechanics/{mechanic_id}`: Update mechanic profile
- `DELETE /mechanics/{mechanic_id}`: Delete mechanic account
- `GET /mechanics/appointments`: Get appointments for the current mechanic

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:
```
Authorization: Bearer your_jwt_token
```


## Swagger Documentation

Access the Swagger UI at `http://localhost:8000/docs` for interactive API documentation.


## Contact

Anton Korinchuk - antonkorinchuk.py@gmail.com
