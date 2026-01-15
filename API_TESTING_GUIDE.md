# API Testing Guide

## Setup for Testing

### 1. Start the Server
```bash
python manage.py runserver
```

### 2. Create Test Data
```bash
python manage.py create_test_data
```

## Test Scenarios

### Authentication Flow

#### 1. Login as Super Admin
**Endpoint**: `POST /api/v1/auth/login/`
```json
{
  "email": "superadmin@gym.com",
  "password": "SuperAdmin@123"
}
```

**Expected**: 200 OK with access and refresh tokens

#### 2. Login as Gym Manager
**Endpoint**: `POST /api/v1/auth/login/`
```json
{
  "email": "manager1@gym.com",
  "password": "Manager@123"
}
```

**Expected**: 200 OK with branch assignment

#### 3. Login as Trainer
**Endpoint**: `POST /api/v1/auth/login/`
```json
{
  "email": "trainer1@gym.com",
  "password": "Trainer@123"
}
```

**Expected**: 200 OK with trainer role

#### 4. Login as Member
**Endpoint**: `POST /api/v1/auth/login/`
```json
{
  "email": "member1@gym.com",
  "password": "Member@123"
}
```

**Expected**: 200 OK with member role

### Authorization Tests

#### ✓ Super Admin Can Create Gym Branch
1. Login as super admin
2. `POST /api/v1/gym-branches/`
3. Expected: 201 Created

#### ✗ Gym Manager Cannot Create Gym Branch
1. Login as manager1
2. `POST /api/v1/gym-branches/`
3. Expected: 403 Forbidden

#### ✓ Gym Manager Can Create Trainer for Their Branch
1. Login as manager1
2. `POST /api/v1/users/`
```json
{
  "email": "newtrainer@gym.com",
  "first_name": "New",
  "last_name": "Trainer",
  "password": "Trainer@123",
  "password_confirm": "Trainer@123",
  "role": "trainer",
  "gym_branch": 1
}
```
3. Expected: 201 Created

#### ✗ Gym Manager Cannot Create Trainer for Another Branch
1. Login as manager1
2. `POST /api/v1/users/` with gym_branch=2
3. Expected: 403 Forbidden

### Business Rule Tests

#### ✓ Maximum 3 Trainers Per Branch
1. Create 4th trainer for same branch
2. Expected: 400 Bad Request with "Maximum 3 trainers allowed"

#### ✓ Cannot Assign Task to Member from Different Branch
1. Login as trainer1 (Downtown)
2. `POST /api/v1/workout-tasks/`
```json
{
  "workout_plan": 1,
  "member": 9,
  "status": "pending",
  "due_date": "2024-02-15T10:00:00Z"
}
```
(member 9 is from Uptown branch)
3. Expected: 403 Forbidden

#### ✓ Member Can Only See Their Own Tasks
1. Login as member1
2. `GET /api/v1/workout-tasks/`
3. Expected: Only member1's tasks in response

#### ✗ Member Cannot Update Another Member's Task
1. Get task ID of member2
2. Login as member1
3. `PATCH /api/v1/workout-tasks/{member2_task_id}/`
4. Expected: 403 Forbidden

#### ✓ Trainer Can Update Task Status
1. Login as trainer1
2. `PATCH /api/v1/workout-tasks/1/`
```json
{
  "status": "in_progress"
}
```
3. Expected: 200 OK

#### ✓ Member Can Only Update Status Field
1. Login as member1
2. `PATCH /api/v1/workout-tasks/1/`
```json
{
  "status": "completed"
}
```
3. Expected: 200 OK

#### ✗ Member Cannot Update Other Fields
1. Login as member1
2. `PATCH /api/v1/workout-tasks/1/`
```json
{
  "member": 2
}
```
3. Expected: 403 Forbidden

### Pagination Tests

#### ✓ List Endpoints Support Pagination
1. `GET /api/v1/users/?page=1&page_size=10`
2. Expected: 200 OK with pagination metadata
```json
{
  "count": 9,
  "next": null,
  "previous": null,
  "results": [...]
}
```

#### ✓ Search Works
1. `GET /api/v1/users/?search=trainer`
2. Expected: Filtered results

#### ✓ Filtering Works
1. `GET /api/v1/users/?role=trainer`
2. Expected: Only trainers returned

### Error Handling Tests

#### ✓ Invalid Credentials
1. `POST /api/v1/auth/login/`
```json
{
  "email": "user@example.com",
  "password": "wrong"
}
```
2. Expected: 400 Bad Request with "Invalid email or password"

#### ✓ Missing Authentication
1. `GET /api/v1/users/` (without Authorization header)
2. Expected: 401 Unauthorized

#### ✓ Invalid Token
1. `GET /api/v1/users/`
   `Authorization: Bearer invalid-token`
2. Expected: 401 Unauthorized

#### ✓ Expired Token
1. Use old refresh token
2. Expected: 400 Bad Request

#### ✓ Resource Not Found
1. `GET /api/v1/gym-branches/999/`
2. Expected: 404 Not Found

### Data Validation Tests

#### ✓ Password Confirmation Must Match
1. `POST /api/v1/users/` with mismatched passwords
2. Expected: 400 Bad Request

#### ✓ Email Must Be Unique
1. Create user with duplicate email
2. Expected: 400 Bad Request

#### ✓ Valid Date Format Required
1. `POST /api/v1/workout-tasks/`
```json
{
  "due_date": "invalid-date"
}
```
2. Expected: 400 Bad Request

## Performance Testing

### N+1 Query Check
Use Django Debug Toolbar or query logging to verify:
- List endpoints don't cause N+1 queries
- Use select_related() for ForeignKeys
- Use prefetch_related() for reverse relations

### Load Testing Commands
```bash
# Test with locust
locust -f locustfile.py

# Test with Apache Bench
ab -n 1000 -c 10 http://localhost:8000/api/v1/users/
```

## Checklist for Complete Testing

- [ ] All 4 user roles can login
- [ ] Super Admin can manage branches
- [ ] Gym Manager can manage users in their branch
- [ ] Trainer can create plans and assign tasks
- [ ] Member can view and update their tasks
- [ ] Branch isolation is enforced
- [ ] 3 trainer limit is enforced
- [ ] Pagination works
- [ ] Filtering works
- [ ] Search works
- [ ] Error messages are clear
- [ ] JWT token refresh works
- [ ] Activity logs are created
- [ ] Invalid inputs are rejected
- [ ] Unauthorized access is blocked
