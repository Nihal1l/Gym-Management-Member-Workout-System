# Quick Start Guide

## 5-Minute Setup

### Option 1: Docker (Fastest)
```bash
docker-compose up --build
```
Then access:
- API: http://localhost:8000/api/v1/
- Admin: http://localhost:8000/admin/
- Swagger: http://localhost:8000/swagger/

### Option 2: Local Setup

#### Step 1: Install
```bash
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate
pip install -r requirements.txt
```

#### Step 2: Database
```bash
python manage.py migrate
python manage.py create_test_data
```

#### Step 3: Run
```bash
python manage.py runserver
```

## Testing the API

### Method 1: Postman (Recommended)
1. Import: `postman/Gym_Management_API.postman_collection.json`
2. Set `base_url` to: `http://localhost:8000`
3. Login with: `superadmin@gym.com` / `SuperAdmin@123`
4. Copy `access` token to `access_token` variable
5. Start testing!

### Method 2: cURL
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@gym.com","password":"SuperAdmin@123"}'

# Get branches (with token)
curl -X GET http://localhost:8000/api/v1/gym-branches/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Method 3: Python
```python
import requests

# Login
response = requests.post('http://localhost:8000/api/v1/auth/login/', json={
    'email': 'superadmin@gym.com',
    'password': 'SuperAdmin@123'
})
token = response.json()['access']

# Make authenticated request
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://localhost:8000/api/v1/gym-branches/', headers=headers)
print(response.json())
```

## Test Users

| Role | Email | Password |
|------|-------|----------|
| Super Admin | superadmin@gym.com | SuperAdmin@123 |
| Manager | manager1@gym.com | Manager@123 |
| Trainer | trainer1@gym.com | Trainer@123 |
| Member | member1@gym.com | Member@123 |

## Quick API Examples

### 1. Login & Get Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@gym.com","password":"SuperAdmin@123"}' | jq .
```

### 2. Create Gym Branch (Super Admin Only)
```bash
curl -X POST http://localhost:8000/api/v1/gym-branches/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Gym",
    "location": "123 Main St"
  }' | jq .
```

### 3. Create Trainer (Manager Only)
```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "trainer@example.com",
    "first_name": "John",
    "last_name": "Trainer",
    "password": "Trainer@123",
    "password_confirm": "Trainer@123",
    "role": "trainer",
    "gym_branch": 1
  }' | jq .
```

### 4. Create Workout Plan (Trainer Only)
```bash
curl -X POST http://localhost:8000/api/v1/workout-plans/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Full Body Workout",
    "description": "Complete routine",
    "gym_branch": 1
  }' | jq .
```

### 5. Assign Task (Trainer Only)
```bash
curl -X POST http://localhost:8000/api/v1/workout-tasks/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workout_plan": 1,
    "member": 7,
    "status": "pending",
    "due_date": "2024-02-15T10:00:00Z"
  }' | jq .
```

### 6. Update Task Status (Member Can Update Own)
```bash
curl -X PATCH http://localhost:8000/api/v1/workout-tasks/1/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}' | jq .
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific test
pytest gym_api/tests.py::TestAuthentication::test_login_with_valid_credentials -v

# With coverage
pytest --cov=gym_api --cov-report=html
```

## Common Issues

### Port Already in Use
```bash
# Change port
python manage.py runserver 8001
```

### Database Error
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
python manage.py create_test_data
```

### Permission Denied (Docker)
```bash
# Run with sudo
sudo docker-compose up
```

### Import Error
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Documentation

- **Main Docs**: See `README.md`
- **API Testing**: See `API_TESTING_GUIDE.md`
- **Deployment**: See `DEPLOYMENT_GUIDE.md`
- **Development**: See `DEVELOPMENT_NOTES.md`
- **Submission**: See `SUBMISSION_SUMMARY.md`

## Next Steps

1. ✅ Server running
2. ✅ Test data created
3. ✅ Users authenticated
4. Now explore with Postman collection!

## Support

All endpoints documented in README.md
Check Postman collection for examples
Review API_TESTING_GUIDE.md for test scenarios

---

**Enjoy! 🚀**
