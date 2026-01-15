# Gym Management API - Development Notes

## Architecture Overview

### Authentication & Authorization

**JWT-Based Authentication**
- Uses `djangorestframework-simplejwt`
- Tokens include user identity and role information
- Access token: 1 hour expiration
- Refresh token: 7 days expiration
- Token rotation enabled for security

**Role-Based Access Control**
1. **Super Admin**: No branch restrictions, can manage entire system
2. **Gym Manager**: Manages single branch, can create trainers/members
3. **Trainer**: Creates workout plans and assigns tasks within branch
4. **Member**: Views and updates own tasks only

### Database Design

**Key Relationships**
- User → GymBranch (Many-to-One)
- WorkoutPlan → User (FK to Trainer), GymBranch
- WorkoutTask → WorkoutPlan, User (Member), User (Created By)

**Performance Optimizations**
- Indexed fields: email, role, gym_branch on User
- Compound indexes: (gym_branch, created_by), (member, status)
- All foreign keys are indexed
- Timestamps indexed for efficient sorting

### API Design Patterns

**RESTful Resources**
```
POST   /api/v1/gym-branches/               Create branch (Super Admin)
GET    /api/v1/gym-branches/               List branches
GET    /api/v1/gym-branches/{id}/          Get branch details
PATCH  /api/v1/gym-branches/{id}/          Update branch
DELETE /api/v1/gym-branches/{id}/          Delete branch

POST   /api/v1/users/                      Create user
GET    /api/v1/users/                      List users
GET    /api/v1/users/{id}/                 Get user details
GET    /api/v1/users/trainers/             List trainers in branch
GET    /api/v1/users/members/              List members in branch

POST   /api/v1/workout-plans/              Create plan
GET    /api/v1/workout-plans/              List plans
GET    /api/v1/workout-plans/{id}/         Get plan details
PATCH  /api/v1/workout-plans/{id}/         Update plan
DELETE /api/v1/workout-plans/{id}/         Delete plan

POST   /api/v1/workout-tasks/              Assign task
GET    /api/v1/workout-tasks/              List tasks
GET    /api/v1/workout-tasks/{id}/         Get task details
PATCH  /api/v1/workout-tasks/{id}/         Update task (status)
DELETE /api/v1/workout-tasks/{id}/         Delete task
```

### Business Rules Implementation

**1. Branch Isolation**
- All queries filtered by `user.gym_branch`
- Super Admin has no restrictions
- Enforced at queryset level (security)

**2. Trainer Limit (Max 3 per branch)**
```python
# In UserCreateSerializer.validate()
trainer_count = User.objects.filter(
    role='trainer',
    gym_branch=gym_branch
).count()
if trainer_count >= 3:
    raise ValidationError("Maximum 3 trainers allowed")
```

**3. Member Task Isolation**
```python
# In WorkoutTaskViewSet.get_queryset()
if user.role == 'member':
    return WorkoutTask.objects.filter(member=user)
```

**4. Cross-Branch Task Prevention**
```python
# In WorkoutTaskViewSet.create()
if member.gym_branch != workout_plan.gym_branch:
    return 403 Forbidden
```

### Error Handling Strategy

**HTTP Status Codes**
- `200 OK`: Successful GET, PATCH
- `201 Created`: Successful POST
- `204 No Content`: DELETE (optional)
- `400 Bad Request`: Validation errors, business rule violations
- `401 Unauthorized`: Missing/invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource doesn't exist
- `500 Server Error`: Database or server error

**Error Response Format**
```json
{
  "error": "Short error message",
  "detail": "Detailed explanation (optional)"
}
```

### Testing Strategy

**Test Coverage Areas**
1. Authentication flows (login, refresh, profile)
2. Role-based permissions (4 roles × endpoints)
3. Business rules (3 trainers, branch isolation, etc.)
4. Data validation (email unique, date format, etc.)
5. Pagination and filtering
6. Error scenarios

**Test Organization**
- `TestAuthentication`: Login and token endpoints
- `TestGymBranch`: Branch CRUD and access control
- `TestUserManagement`: User creation and filtering
- `TestWorkoutTasks`: Task assignment and updates

### Performance Considerations

**N+1 Query Prevention**
- Use `select_related()` for direct ForeignKeys
- Use `prefetch_related()` for reverse relations
- Verified in test environment

**Pagination**
- Default page size: 20 items
- Configurable via `page_size` query parameter
- Limits: 1-100 items per page

**Database Indexes**
- Primary keys (automatic)
- Foreign keys (automatic)
- Composite indexes: (gym_branch, created_by), (member, status)

### Security Measures

**1. Password Security**
- Hashed with Django's PBKDF2
- Min 8 characters recommended
- No password transmitted in API responses

**2. Token Security**
- JWT tokens signed with `SECRET_KEY`
- Refresh token rotation enabled
- Tokens have expiration times

**3. Input Validation**
- Email format validated
- Role restricted to 4 choices
- Status values: pending, in_progress, completed

**4. SQL Injection Protection**
- All queries use ORM (parameterized)
- No raw SQL in views

**5. CORS Configuration**
- Configurable allowed origins
- Credentials allowed
- Prevents unauthorized cross-origin requests

### Deployment Considerations

**Configuration Management**
- All secrets in environment variables
- DEBUG=False in production
- Separate requirements files (dev vs prod)

**Database**
- Supports SQLite (dev) and PostgreSQL (prod)
- Migrations included
- Connection pooling recommended for production

**Static Files**
- Collected via `collectstatic`
- Served by Nginx in production
- Can use CDN for assets

**Monitoring**
- Activity logs for audit trail
- Django logging framework
- Can integrate with Sentry/Datadog

## Development Workflow

### Local Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run migrations
python manage.py migrate

# 3. Create test data
python manage.py create_test_data

# 4. Start development server
python manage.py runserver
```

### Testing
```bash
# Run all tests
pytest

# Run specific test class
pytest gym_api/tests.py::TestAuthentication -v

# Generate coverage report
pytest --cov=gym_api --cov-report=html
```

### Making Changes
1. Create feature branch: `git checkout -b feature/description`
2. Make changes
3. Run tests: `pytest`
4. Run linter: `flake8 gym_api`
5. Commit: `git commit -m "Feature: description"`
6. Push: `git push origin feature/description`
7. Create pull request for review

## Common Tasks

### Add New Endpoint
1. Create serializer in `serializers.py`
2. Create viewset in `views.py`
3. Register route in `urls.py`
4. Add permission class
5. Write tests

### Modify User Roles
1. Edit `User.ROLE_CHOICES` in `models.py`
2. Update permission classes if needed
3. Update tests
4. Create migration: `python manage.py makemigrations`

### Add New Field to Model
1. Add field to model in `models.py`
2. Update serializer in `serializers.py`
3. Create migration: `python manage.py makemigrations`
4. Run migration: `python manage.py migrate`
5. Update tests

### Deploy New Version
1. Run migrations on production
2. Collect static files
3. Restart application server
4. Verify with Postman collection

## Troubleshooting

### Common Issues

**CORS Error**
- Check `CORS_ALLOWED_ORIGINS` in settings.py
- Ensure frontend URL is included
- Restart server

**Authentication Error (401)**
- Verify token in Authorization header
- Check token expiration
- Try refreshing token

**Permission Error (403)**
- Verify user role
- Check gym_branch assignment
- Verify user is active

**Database Error**
- Check database connection
- Verify credentials in .env
- Run migrations: `python manage.py migrate`

**Test Failures**
- Clear test database: `pytest --create-db`
- Recreate test data: `python manage.py create_test_data`
- Check database migrations

## Future Enhancements

1. **Performance**
   - Add Redis caching for frequently accessed data
   - Implement rate limiting

2. **Features**
   - Progress tracking on tasks
   - Email notifications
   - File attachments for tasks

3. **Security**
   - Two-factor authentication
   - API key authentication
   - IP whitelisting

4. **Monitoring**
   - Structured logging with ELK
   - Application performance monitoring
   - Error tracking with Sentry

5. **Testing**
   - Performance testing with Locust
   - Load testing
   - Security scanning

---

**Last Updated**: January 2024
**Maintainer**: Development Team
