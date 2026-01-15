# Gym Management & Member Workout System - REST API

A comprehensive Django REST Framework backend for managing gym branches, trainers, members, and workout plans with role-based access control and JWT authentication.

## 📋 Project Overview

This is a complete REST API backend (no frontend) designed for internal use by fitness companies to manage:
- Multiple gym branches
- Trainers assigned to branches
- Members with gym memberships
- Workout plans created by trainers
- Workout tasks assigned to members

## 🏗️ System Architecture

### User Roles & Permissions

#### 1. **Super Admin**
- Create and manage gym branches
- View all data across branches (no branch restrictions)
- Create gym managers
- View all users and activities
- Access activity logs

#### 2. **Gym Manager**
- Manage one gym branch
- Create trainers (max 3 per branch)
- Create members
- View all members and trainers in their branch
- View all workout plans and tasks in their branch
- Cannot create other managers or super admins

#### 3. **Trainer**
- Belongs to one gym branch
- Create workout plans for their branch
- Assign workout tasks to members in their branch
- Update task status
- View all tasks in their branch
- Cannot assign tasks to members from other branches

#### 4. **Member**
- Belongs to one gym branch
- View only their assigned workout tasks
- Update their own task status (pending → in_progress → completed)
- Cannot view workout plans directly
- Cannot access other members' tasks

### Core Entities

```
User
├── email (unique)
├── password (hashed)
├── role (super_admin, gym_manager, trainer, member)
├── gym_branch (nullable for super_admin)
├── first_name
├── last_name
└── created_at

GymBranch
├── name
├── location
├── is_active
└── created_at

WorkoutPlan
├── title
├── description
├── created_by (Trainer)
├── gym_branch
└── created_at

WorkoutTask
├── workout_plan (FK)
├── member (FK)
├── status (pending, in_progress, completed)
├── due_date
├── created_by (Trainer)
└── created_at

ActivityLog (audit trail)
├── user
├── action
├── model_name
├── changes
└── created_at
```

## 🔒 Security & Business Rules

### Strict Enforcement

1. **Branch Isolation**: Users can only access data from their assigned branch (except Super Admin)
2. **Trainer Limit**: Maximum 3 trainers per gym branch
3. **Task Assignment**: Trainers cannot assign tasks to members from other branches
4. **Member Privacy**: Members cannot view or update other members' tasks
5. **Role-Based Access**: All APIs enforce role-based authorization
6. **JWT Authentication**: All endpoints (except login) require valid JWT token

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (optional, SQLite for development)
- Docker & Docker Compose (optional)

### Local Development Setup

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd gym-management-system
```

#### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Setup Environment Variables
```bash
# Copy example file
cp .env.example .env

# Update .env with your configuration
# For local development, defaults are fine
```

#### 5. Run Migrations
```bash
python manage.py migrate
```

#### 6. Create Test Data
```bash
python manage.py create_test_data
```

This will create:
- 1 Super Admin
- 2 Gym Managers (one per branch)
- 3 Trainers (2 in downtown, 1 in uptown)
- 3 Members (2 in downtown, 1 in uptown)
- 2 Gym Branches
- Sample workout plans and tasks

#### 7. Run Development Server
```bash
python manage.py runserver
```

API will be available at: `http://localhost:8000/api/v1/`

### Using Docker

#### 1. Build and Run with Docker Compose
```bash
docker-compose up --build
```

This will:
- Start PostgreSQL database
- Run migrations
- Create test data
- Start Django development server

#### 2. Access the API
- API: `http://localhost:8000/api/v1/`
- Admin Panel: `http://localhost:8000/admin/`
- API Documentation: `http://localhost:8000/swagger/`

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/v1/
```

### Authentication Endpoints

#### 1. Login
```http
POST /auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "Password@123"
}

Response:
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "trainer",
    "gym_branch": 1,
    "is_active": true
  }
}
```

#### 2. Refresh Token
```http
POST /auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

Response:
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### 3. Get Profile
```http
GET /auth/profile/
Authorization: Bearer {access_token}

Response:
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "trainer",
  "gym_branch": 1,
  "is_active": true
}
```

### Gym Branch Endpoints

#### Create Branch (Super Admin Only)
```http
POST /gym-branches/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "New Branch",
  "location": "123 Main St",
  "is_active": true
}
```

#### List Branches
```http
GET /gym-branches/?page=1&page_size=20
Authorization: Bearer {access_token}
```

#### Get Branch Details
```http
GET /gym-branches/{id}/
Authorization: Bearer {access_token}
```

#### Update Branch (Super Admin Only)
```http
PATCH /gym-branches/{id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "is_active": true
}
```

#### Delete Branch (Super Admin Only)
```http
DELETE /gym-branches/{id}/
Authorization: Bearer {access_token}
```

### User Management Endpoints

#### Create User (Manager or Super Admin)
```http
POST /users/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "email": "newuser@gym.com",
  "first_name": "John",
  "last_name": "Trainer",
  "password": "Password@123",
  "password_confirm": "Password@123",
  "role": "trainer",
  "gym_branch": 1
}
```

#### List Users
```http
GET /users/?page=1&role=trainer&gym_branch=1
Authorization: Bearer {access_token}
```

#### List Trainers in Branch
```http
GET /users/trainers/
Authorization: Bearer {access_token}
```

#### List Members in Branch
```http
GET /users/members/
Authorization: Bearer {access_token}
```

### Workout Plan Endpoints

#### Create Plan (Trainer Only)
```http
POST /workout-plans/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "Full Body Workout",
  "description": "Complete workout routine",
  "gym_branch": 1
}
```

#### List Plans
```http
GET /workout-plans/?page=1&gym_branch=1
Authorization: Bearer {access_token}
```

#### Update Plan (Creator Only)
```http
PATCH /workout-plans/{id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "Updated Title",
  "description": "Updated description"
}
```

### Workout Task Endpoints

#### Assign Task (Trainer Only)
```http
POST /workout-tasks/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "workout_plan": 1,
  "member": 7,
  "status": "pending",
  "due_date": "2024-02-15T10:00:00Z"
}
```

#### List Tasks
```http
GET /workout-tasks/?status=pending&page=1
Authorization: Bearer {access_token}
```

#### Update Task Status
```http
PATCH /workout-tasks/{id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "status": "in_progress"
}

Valid values: pending, in_progress, completed
```

## 👥 Test User Credentials

### Pre-created Users (from `create_test_data` command):

| Role | Email | Password | Branch |
|------|-------|----------|--------|
| Super Admin | superadmin@gym.com | SuperAdmin@123 | - |
| Manager | manager1@gym.com | Manager@123 | Downtown |
| Manager | manager2@gym.com | Manager@123 | Uptown |
| Trainer | trainer1@gym.com | Trainer@123 | Downtown |
| Trainer | trainer2@gym.com | Trainer@123 | Downtown |
| Trainer | trainer3@gym.com | Trainer@123 | Uptown |
| Member | member1@gym.com | Member@123 | Downtown |
| Member | member2@gym.com | Member@123 | Downtown |
| Member | member3@gym.com | Member@123 | Uptown |

## 📮 Postman Collection

A complete Postman collection is provided for testing all API endpoints.

### Import Collection
1. Open Postman
2. Click "Import" → "Upload Files"
3. Select `postman/Gym_Management_API.postman_collection.json`

### Setup Environment Variables
1. In Postman, create an environment with:
   - `base_url`: `http://localhost:8000`
   - `access_token`: (set after login)
   - `refresh_token`: (set after login)

### Testing Workflow
1. Login with a test user (Authentication → Login)
2. Copy the `access` token from response
3. Set `access_token` variable in Postman
4. Test other endpoints

## 📊 Database Schema & ER Diagram

### Entity Relationships

```
┌─────────────────────────┐
│       User              │
├─────────────────────────┤
│ id (PK)                 │
│ email (UNIQUE)          │
│ role                    │
│ gym_branch (FK)         │
│ password_hash           │
│ created_at              │
└─────────────────────────┘
         │
         │ (1:N)
         ▼
┌─────────────────────────┐
│     GymBranch           │
├─────────────────────────┤
│ id (PK)                 │
│ name                    │
│ location                │
│ created_at              │
└─────────────────────────┘

┌─────────────────────────┐         ┌──────────────────────┐
│   WorkoutPlan           │◄────────│   WorkoutTask        │
├─────────────────────────┤         ├──────────────────────┤
│ id (PK)                 │ (1:N)   │ id (PK)              │
│ title                   │         │ workout_plan (FK)    │
│ description             │         │ member (FK)          │
│ created_by (FK-User)    │         │ status               │
│ gym_branch (FK)         │         │ due_date             │
│ created_at              │         │ created_by (FK)      │
└─────────────────────────┘         │ created_at           │
                                    └──────────────────────┘

┌──────────────────────────┐
│    ActivityLog           │
├──────────────────────────┤
│ id (PK)                  │
│ user (FK)                │
│ action                   │
│ model_name               │
│ object_id                │
│ changes (JSON)           │
│ created_at               │
└──────────────────────────┘
```

### Key Indexes
- User: email, role, gym_branch
- GymBranch: name, is_active
- WorkoutPlan: gym_branch + created_by, created_at
- WorkoutTask: member + status, workout_plan + member, created_at, due_date
- ActivityLog: user + created_at, created_at

## 🧪 Testing

### Run Unit Tests
```bash
pytest
```

### Run Tests with Coverage
```bash
pytest --cov=gym_api
```

### Run Specific Test File
```bash
pytest gym_api/tests.py -v
```

## 🔧 Project Structure

```
gym-management-system/
├── gym_management/           # Main project settings
│   ├── settings.py          # Django settings
│   ├── urls.py              # URL routing
│   ├── wsgi.py              # WSGI app
│   └── asgi.py              # ASGI app
├── gym_api/                  # Main API app
│   ├── models.py            # Database models
│   ├── serializers.py       # DRF serializers
│   ├── views.py             # ViewSets and views
│   ├── permissions.py       # Custom permission classes
│   ├── admin.py             # Django admin config
│   ├── urls.py              # API routes
│   ├── management/          # Management commands
│   │   └── commands/
│   │       └── create_test_data.py
│   └── migrations/          # Database migrations
├── postman/                  # Postman collection
│   └── Gym_Management_API.postman_collection.json
├── requirements.txt         # Python dependencies
├── manage.py               # Django management
├── Dockerfile              # Docker config
├── docker-compose.yml      # Docker Compose config
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🔄 API Response Format

### Success Response (200, 201)
```json
{
  "id": 1,
  "field1": "value1",
  "field2": "value2"
}
```

### List Response with Pagination
```json
{
  "count": 100,
  "next": "http://api.example.com/resource/?page=2",
  "previous": null,
  "results": [
    { "id": 1, "field": "value" },
    { "id": 2, "field": "value" }
  ]
}
```

### Error Response (400, 403, 404)
```json
{
  "error": "Error message",
  "detail": "Detailed error explanation"
}
```

## 🛡️ Authorization Errors

| Status | Scenario |
|--------|----------|
| 401 | Missing or invalid JWT token |
| 403 | User lacks permission for this action |
| 404 | Resource not found |
| 400 | Invalid input or business rule violation |

## 📦 Deployment

### Environment Variables Required
```
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=gym_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=db-host
DB_PORT=5432
JWT_SECRET_KEY=your-jwt-secret
CORS_ALLOWED_ORIGINS=https://your-frontend.com
```

### Deploy to Cloud

#### Heroku
```bash
heroku create your-app-name
heroku config:set SECRET_KEY=your-secret-key
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py create_test_data
```

#### AWS/DigitalOcean/Other
- Update `ALLOWED_HOSTS` in settings.py
- Set environment variables on host
- Run migrations: `python manage.py migrate`
- Collect static files: `python manage.py collectstatic`
- Use Gunicorn/uWSGI as WSGI server

## 📝 Logging

Activity logs are automatically created for:
- User login
- Resource creation, updates, and deletions

Access logs via:
```http
GET /activity-logs/
Authorization: Bearer {super_admin_token}
```

## 💾 Database Dump

### Export Database
```bash
# SQLite
python manage.py dumpdata > db_dump.json

# PostgreSQL
pg_dump gym_db > db_dump.sql
```

### Import Database
```bash
# SQLite
python manage.py loaddata db_dump.json

# PostgreSQL
psql gym_db < db_dump.sql
```

## 🐛 Troubleshooting

### Migration Errors
```bash
# Reset migrations (development only!)
python manage.py migrate gym_api zero
python manage.py makemigrations
python manage.py migrate
```

### Clear Test Data
```bash
python manage.py flush
python manage.py create_test_data
```

### Check Database Connection
```bash
python manage.py dbshell
```

## 📧 Support

For issues or questions, please contact the development team.

## 📄 License

This project is proprietary and for internal use only.

## ✅ Checklist

- [x] JWT authentication with access/refresh tokens
- [x] Role-based access control (4 roles)
- [x] Branch isolation enforcement
- [x] 3 trainers per branch limit
- [x] Complete CRUD operations for all entities
- [x] Task status management
- [x] Activity logging
- [x] Input validation
- [x] Proper error handling
- [x] Pagination for list endpoints
- [x] Docker support
- [x] Postman collection
- [x] Database schema with indexes
- [x] Test data generation

---

**Version**: 1.0.0  
**Last Updated**: January 2024
