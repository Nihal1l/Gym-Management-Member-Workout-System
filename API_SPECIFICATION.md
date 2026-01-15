# API Specification & Reference

## Base URL
```
http://localhost:8000/api/v1/
```

## Authentication

All endpoints except login require JWT Bearer token in Authorization header:
```
Authorization: Bearer <access_token>
```

### Auth Endpoints

#### POST /auth/login/
Login with email and password, returns access and refresh tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "Password@123"
}
```

**Response:** 200 OK
```json
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
    "gym_branch_detail": {
      "id": 1,
      "name": "Downtown Gym",
      "location": "123 Main St"
    },
    "is_active": true,
    "created_at": "2024-01-15T10:00:00Z"
  }
}
```

**Errors:**
- 400: Invalid email or password
- 400: User account is inactive

---

#### POST /auth/refresh/
Refresh access token using refresh token.

**Request:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** 200 OK
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Errors:**
- 400: Invalid refresh token
- 400: Token is expired

---

#### GET /auth/profile/
Get current user's profile information.

**Response:** 200 OK
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "trainer",
  "gym_branch": 1,
  "gym_branch_detail": { ... },
  "is_active": true,
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

## Gym Branch Endpoints

### GET /gym-branches/
List all gym branches (with pagination).

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `page_size` (integer): Items per page (default: 20, max: 100)
- `search` (string): Search by name or location
- `ordering` (string): Sort by field (e.g., `-created_at`)

**Response:** 200 OK
```json
{
  "count": 5,
  "next": "http://localhost:8000/api/v1/gym-branches/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Downtown Gym",
      "location": "123 Main St",
      "is_active": true,
      "trainer_count": 3,
      "member_count": 15,
      "created_at": "2024-01-10T08:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

**Permissions:** All authenticated users (but filtered by branch for non-admins)

---

### POST /gym-branches/
Create a new gym branch.

**Permissions:** Super Admin only

**Request:**
```json
{
  "name": "New Gym Location",
  "location": "456 Oak Ave",
  "is_active": true
}
```

**Response:** 201 Created
```json
{
  "id": 2,
  "name": "New Gym Location",
  "location": "456 Oak Ave",
  "is_active": true,
  "trainer_count": 0,
  "member_count": 0,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

**Errors:**
- 403: Only super admin can create branches
- 400: Invalid input (missing required fields)

---

### GET /gym-branches/{id}/
Get gym branch details.

**Response:** 200 OK
```json
{
  "id": 1,
  "name": "Downtown Gym",
  "location": "123 Main St",
  "is_active": true,
  "trainer_count": 3,
  "member_count": 15,
  "created_at": "2024-01-10T08:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

**Errors:**
- 404: Branch not found
- 403: Access denied (not in your branch)

---

### PATCH /gym-branches/{id}/
Update gym branch.

**Permissions:** Super Admin only

**Request:**
```json
{
  "is_active": false
}
```

**Response:** 200 OK (updated object)

**Errors:**
- 403: Only super admin can update
- 404: Not found
- 400: Invalid input

---

### DELETE /gym-branches/{id}/
Delete gym branch.

**Permissions:** Super Admin only

**Response:** 204 No Content

**Errors:**
- 403: Only super admin can delete
- 404: Not found

---

## User Endpoints

### GET /users/
List users (with pagination).

**Permissions:**
- Super Admin: All users
- Manager: Users in their branch
- Others: Only themselves

**Query Parameters:**
- `page`, `page_size` (pagination)
- `role` (filter): super_admin, gym_manager, trainer, member
- `gym_branch` (filter): Branch ID
- `search`: Search by email, first_name, last_name
- `ordering`: Sort by field

**Response:** 200 OK
```json
{
  "count": 9,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Trainer",
      "role": "trainer",
      "gym_branch": 1,
      "is_active": true,
      "created_at": "2024-01-10T08:00:00Z"
    }
  ]
}
```

---

### POST /users/
Create a new user.

**Permissions:**
- Super Admin: Can create any user
- Manager: Can create trainers and members for their branch

**Request:**
```json
{
  "email": "newuser@example.com",
  "first_name": "Jane",
  "last_name": "Trainer",
  "password": "SecurePass@123",
  "password_confirm": "SecurePass@123",
  "role": "trainer",
  "gym_branch": 1
}
```

**Response:** 201 Created
```json
{
  "id": 10,
  "email": "newuser@example.com",
  "first_name": "Jane",
  "last_name": "Trainer",
  "role": "trainer",
  "gym_branch": 1,
  "is_active": true,
  "created_at": "2024-01-15T10:00:00Z"
}
```

**Validation Rules:**
- Email must be unique
- Password min 8 characters
- password must equal password_confirm
- Super Admin cannot have gym_branch
- Non-admins must have gym_branch
- Max 3 trainers per branch

**Errors:**
- 403: Permission denied for role/branch
- 400: Validation error (see details)
- 400: Max trainers exceeded

---

### GET /users/{id}/
Get user details.

**Response:** 200 OK
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Trainer",
  "role": "trainer",
  "gym_branch": 1,
  "gym_branch_detail": {
    "id": 1,
    "name": "Downtown Gym",
    "location": "123 Main St"
  },
  "is_active": true,
  "created_at": "2024-01-10T08:00:00Z"
}
```

---

### GET /users/trainers/
List trainers in user's branch.

**Permissions:** Manager and Trainer only

**Response:** 200 OK
```json
[
  {
    "id": 2,
    "email": "trainer1@example.com",
    "first_name": "Mike",
    "last_name": "Trainer",
    "role": "trainer",
    "gym_branch": 1,
    "is_active": true,
    "created_at": "2024-01-10T08:00:00Z"
  }
]
```

---

### GET /users/members/
List members in user's branch.

**Permissions:** Manager and Trainer only

**Response:** 200 OK (list of members)

---

## Workout Plan Endpoints

### POST /workout-plans/
Create workout plan.

**Permissions:** Trainer only

**Request:**
```json
{
  "title": "Full Body Workout",
  "description": "Complete workout routine for beginners",
  "gym_branch": 1
}
```

**Response:** 201 Created
```json
{
  "id": 1,
  "title": "Full Body Workout",
  "description": "Complete workout routine for beginners",
  "created_by": 2,
  "created_by_detail": {
    "id": 2,
    "email": "trainer@example.com",
    "first_name": "Mike",
    "last_name": "Trainer",
    "role": "trainer",
    "gym_branch": 1,
    "is_active": true,
    "created_at": "2024-01-10T08:00:00Z"
  },
  "gym_branch": 1,
  "task_count": 0,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

**Errors:**
- 403: Only trainers can create plans
- 400: Gym branch required

---

### GET /workout-plans/
List workout plans.

**Permissions:** Trainer and Manager (see only their branch)

**Query Parameters:**
- `page`, `page_size`
- `gym_branch` (filter)
- `created_by` (filter)
- `search`: Search by title or description
- `ordering`

**Response:** 200 OK (paginated list)

---

### PATCH /workout-plans/{id}/
Update workout plan.

**Permissions:** Creator (Trainer) only

**Request:**
```json
{
  "title": "Updated Title",
  "description": "Updated description"
}
```

**Response:** 200 OK (updated object)

---

### DELETE /workout-plans/{id}/
Delete workout plan.

**Permissions:** Creator (Trainer) only

**Response:** 204 No Content

---

## Workout Task Endpoints

### POST /workout-tasks/
Assign workout task to member.

**Permissions:** Trainer only

**Request:**
```json
{
  "workout_plan": 1,
  "member": 7,
  "status": "pending",
  "due_date": "2024-02-15T10:00:00Z"
}
```

**Response:** 201 Created
```json
{
  "id": 1,
  "workout_plan": 1,
  "workout_plan_detail": {
    "id": 1,
    "title": "Full Body Workout",
    "description": "..."
  },
  "member": 7,
  "member_detail": {
    "id": 7,
    "email": "member@example.com",
    "first_name": "Tom",
    "last_name": "Member",
    "role": "member",
    "gym_branch": 1,
    "is_active": true,
    "created_at": "2024-01-10T08:00:00Z"
  },
  "status": "pending",
  "due_date": "2024-02-15T10:00:00Z",
  "created_by": 2,
  "created_by_detail": { ... },
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

**Business Rules:**
- Member must be from same branch
- Trainer must be from same branch
- Status must be one of: pending, in_progress, completed

**Errors:**
- 403: Only trainers can assign tasks
- 403: Cannot assign to member from different branch
- 400: Validation error

---

### GET /workout-tasks/
List workout tasks.

**Permissions:**
- Trainer/Manager: All tasks in their branch
- Member: Only their own tasks

**Query Parameters:**
- `page`, `page_size`
- `status` (filter): pending, in_progress, completed
- `member` (filter): Member ID
- `workout_plan` (filter): Plan ID
- `search`: Search by member email or plan title
- `ordering`: Sort by field

**Response:** 200 OK (paginated list)

---

### PATCH /workout-tasks/{id}/
Update task status.

**Permissions:**
- Trainer: Can update any task in their branch
- Member: Can only update their own task (status only)

**Request:**
```json
{
  "status": "completed"
}
```

**Valid Status Values:**
- `pending`: Not started
- `in_progress`: Currently being worked on
- `completed`: Finished

**Response:** 200 OK (updated object)

**Errors:**
- 403: Permission denied
- 400: Invalid status value

---

### DELETE /workout-tasks/{id}/
Delete workout task.

**Permissions:** Creator (Trainer) only

**Response:** 204 No Content

---

## Activity Log Endpoints

### GET /activity-logs/
List activity logs (audit trail).

**Permissions:** Super Admin only

**Query Parameters:**
- `page`, `page_size`
- `user` (filter): User ID
- `action` (filter): create, update, delete, login
- `model_name` (filter): Model name
- `ordering`

**Response:** 200 OK
```json
{
  "count": 100,
  "results": [
    {
      "id": 1,
      "user": 1,
      "action": "login",
      "model_name": "User",
      "object_id": "1",
      "changes": {},
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

---

## Error Responses

### Standard Error Format
```json
{
  "error": "Error message",
  "detail": "Optional detailed explanation"
}
```

### Common Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Successful GET, PATCH |
| 201 | Created - Successful POST |
| 204 | No Content - Successful DELETE |
| 400 | Bad Request - Validation error |
| 401 | Unauthorized - Missing/invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 500 | Server Error - Internal error |

### Validation Error Example
```json
{
  "email": ["This field may not be blank."],
  "gym_branch": ["Gym branch must be selected for non-admin users"]
}
```

---

## Pagination Format

All list endpoints return paginated results:

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/v1/resource/?page=2",
  "previous": null,
  "results": [ ... ]
}
```

**Parameters:**
- `page` (integer): Page number (default: 1)
- `page_size` (integer): Items per page (default: 20, max: 100)

---

## Filtering & Searching

### Example Queries

```
# Filter by role
GET /users/?role=trainer

# Filter by status
GET /workout-tasks/?status=completed

# Search
GET /users/?search=john

# Combine filters
GET /workout-tasks/?status=pending&member=7

# Pagination
GET /gym-branches/?page=2&page_size=10

# Ordering
GET /users/?ordering=-created_at

# Reverse order
GET /users/?ordering=email
```

---

## Timestamps

All timestamps are in ISO 8601 format with UTC timezone:
```
2024-01-15T10:00:00Z
```

---

## Rate Limiting

Currently no rate limiting. For production, configure in settings.py:
```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

---

## CORS

By default, CORS is enabled for localhost. For production, update:
```python
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
]
```

---

**Last Updated**: January 2024
