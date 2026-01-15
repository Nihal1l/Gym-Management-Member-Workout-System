import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from gym_api.models import GymBranch, WorkoutPlan, WorkoutTask
from datetime import datetime, timedelta

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def super_admin(db):
    return User.objects.create_user(
        email='admin@test.com',
        username='admin',
        password='Admin@123',
        role='super_admin'
    )


@pytest.fixture
def gym_branch(db):
    return GymBranch.objects.create(
        name='Test Gym',
        location='123 Main St'
    )


@pytest.fixture
def gym_manager(db, gym_branch):
    return User.objects.create_user(
        email='manager@test.com',
        username='manager',
        password='Manager@123',
        role='gym_manager',
        gym_branch=gym_branch
    )


@pytest.fixture
def trainer(db, gym_branch):
    return User.objects.create_user(
        email='trainer@test.com',
        username='trainer',
        password='Trainer@123',
        role='trainer',
        gym_branch=gym_branch
    )


@pytest.fixture
def member(db, gym_branch):
    return User.objects.create_user(
        email='member@test.com',
        username='member',
        password='Member@123',
        role='member',
        gym_branch=gym_branch
    )


@pytest.fixture
def workout_plan(db, trainer, gym_branch):
    return WorkoutPlan.objects.create(
        title='Test Plan',
        description='Test Description',
        created_by=trainer,
        gym_branch=gym_branch
    )


@pytest.mark.django_db
class TestAuthentication:
    """Test authentication endpoints"""

    def test_login_with_valid_credentials(self, api_client, gym_manager):
        response = api_client.post('/api/v1/auth/login/', {
            'email': 'manager@test.com',
            'password': 'Manager@123'
        })
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['email'] == 'manager@test.com'

    def test_login_with_invalid_credentials(self, api_client, gym_manager):
        response = api_client.post('/api/v1/auth/login/', {
            'email': 'manager@test.com',
            'password': 'wrong_password'
        })
        assert response.status_code == 400

    def test_get_profile(self, api_client, gym_manager):
        api_client.force_authenticate(user=gym_manager)
        response = api_client.get('/api/v1/auth/profile/')
        assert response.status_code == 200
        assert response.data['email'] == 'manager@test.com'


@pytest.mark.django_db
class TestGymBranch:
    """Test gym branch endpoints"""

    def test_super_admin_can_create_branch(self, api_client, super_admin):
        api_client.force_authenticate(user=super_admin)
        response = api_client.post('/api/v1/gym-branches/', {
            'name': 'New Gym',
            'location': '456 Oak Ave'
        })
        assert response.status_code == 201

    def test_manager_cannot_create_branch(self, api_client, gym_manager):
        api_client.force_authenticate(user=gym_manager)
        response = api_client.post('/api/v1/gym-branches/', {
            'name': 'New Gym',
            'location': '456 Oak Ave'
        })
        assert response.status_code == 403

    def test_list_branches(self, api_client, super_admin):
        api_client.force_authenticate(user=super_admin)
        response = api_client.get('/api/v1/gym-branches/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestUserManagement:
    """Test user management endpoints"""

    def test_manager_can_create_trainer(self, api_client, gym_manager, gym_branch):
        api_client.force_authenticate(user=gym_manager)
        response = api_client.post('/api/v1/users/', {
            'email': 'newtrainer@test.com',
            'first_name': 'New',
            'last_name': 'Trainer',
            'password': 'Trainer@123',
            'password_confirm': 'Trainer@123',
            'role': 'trainer',
            'gym_branch': gym_branch.id
        })
        assert response.status_code == 201

    def test_manager_cannot_create_trainer_for_different_branch(self, api_client, gym_manager, db):
        api_client.force_authenticate(user=gym_manager)
        other_branch = GymBranch.objects.create(
            name='Other Gym',
            location='789 Pine St'
        )
        response = api_client.post('/api/v1/users/', {
            'email': 'newtrainer@test.com',
            'first_name': 'New',
            'last_name': 'Trainer',
            'password': 'Trainer@123',
            'password_confirm': 'Trainer@123',
            'role': 'trainer',
            'gym_branch': other_branch.id
        })
        assert response.status_code == 403

    def test_max_3_trainers_per_branch(self, api_client, gym_manager, gym_branch):
        # Create 3 trainers first
        for i in range(3):
            User.objects.create_user(
                email=f'trainer{i}@test.com',
                username=f'trainer{i}',
                password='Trainer@123',
                role='trainer',
                gym_branch=gym_branch
            )

        api_client.force_authenticate(user=gym_manager)
        response = api_client.post('/api/v1/users/', {
            'email': 'trainer4@test.com',
            'first_name': 'Trainer',
            'last_name': 'Four',
            'password': 'Trainer@123',
            'password_confirm': 'Trainer@123',
            'role': 'trainer',
            'gym_branch': gym_branch.id
        })
        assert response.status_code == 400


@pytest.mark.django_db
class TestWorkoutTasks:
    """Test workout task endpoints"""

    def test_member_can_view_own_tasks(self, api_client, member, workout_plan):
        WorkoutTask.objects.create(
            workout_plan=workout_plan,
            member=member,
            status='pending',
            due_date=datetime.now() + timedelta(days=7),
            created_by=workout_plan.created_by
        )
        api_client.force_authenticate(user=member)
        response = api_client.get('/api/v1/workout-tasks/')
        assert response.status_code == 200
        assert len(response.data['results']) == 1

    def test_trainer_can_assign_task(self, api_client, trainer, member, workout_plan):
        api_client.force_authenticate(user=trainer)
        response = api_client.post('/api/v1/workout-tasks/', {
            'workout_plan': workout_plan.id,
            'member': member.id,
            'status': 'pending',
            'due_date': (datetime.now() + timedelta(days=7)).isoformat()
        })
        assert response.status_code == 201

    def test_trainer_cannot_assign_task_to_member_from_other_branch(
        self, api_client, trainer, db
    ):
        other_branch = GymBranch.objects.create(
            name='Other Gym',
            location='999 Elm St'
        )
        other_trainer = User.objects.create_user(
            email='other_trainer@test.com',
            username='other_trainer',
            password='Trainer@123',
            role='trainer',
            gym_branch=other_branch
        )
        other_member = User.objects.create_user(
            email='other_member@test.com',
            username='other_member',
            password='Member@123',
            role='member',
            gym_branch=other_branch
        )
        other_plan = WorkoutPlan.objects.create(
            title='Other Plan',
            description='Other Description',
            created_by=other_trainer,
            gym_branch=other_branch
        )

        api_client.force_authenticate(user=trainer)
        response = api_client.post('/api/v1/workout-tasks/', {
            'workout_plan': other_plan.id,
            'member': other_member.id,
            'status': 'pending',
            'due_date': (datetime.now() + timedelta(days=7)).isoformat()
        })
        assert response.status_code == 403

    def test_member_can_update_own_task_status(self, api_client, member, workout_plan):
        task = WorkoutTask.objects.create(
            workout_plan=workout_plan,
            member=member,
            status='pending',
            due_date=datetime.now() + timedelta(days=7),
            created_by=workout_plan.created_by
        )
        api_client.force_authenticate(user=member)
        response = api_client.patch(f'/api/v1/workout-tasks/{task.id}/', {
            'status': 'completed'
        })
        assert response.status_code == 200
        task.refresh_from_db()
        assert task.status == 'completed'
