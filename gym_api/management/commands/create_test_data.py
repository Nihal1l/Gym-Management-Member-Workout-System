from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from gym_api.models import GymBranch, WorkoutPlan, WorkoutTask
from datetime import datetime, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test data for the Gym Management system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Creating test data...'))
        
        # Create Gym Branches
        branch1, _ = GymBranch.objects.get_or_create(
            name='Downtown Gym',
            defaults={'location': '123 Main St, City Center'}
        )
        branch2, _ = GymBranch.objects.get_or_create(
            name='Uptown Gym',
            defaults={'location': '456 Oak Ave, Uptown'}
        )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {2} gym branches'))
        
        # Create Super Admin
        if not User.objects.filter(email='superadmin@gym.com').exists():
            User.objects.create_user(
                email='superadmin@gym.com',
                username='superadmin',
                password='SuperAdmin@123',
                first_name='Super',
                last_name='Admin',
                role='super_admin'
            )
        
        # Create Gym Managers
        if not User.objects.filter(email='manager1@gym.com').exists():
            User.objects.create_user(
                email='manager1@gym.com',
                username='manager1',
                password='Manager@123',
                first_name='John',
                last_name='Manager',
                role='gym_manager',
                gym_branch=branch1
            )
        
        if not User.objects.filter(email='manager2@gym.com').exists():
            User.objects.create_user(
                email='manager2@gym.com',
                username='manager2',
                password='Manager@123',
                first_name='Jane',
                last_name='Manager',
                role='gym_manager',
                gym_branch=branch2
            )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {3} users (1 Super Admin, 2 Managers)'))
        
        # Create Trainers
        trainers = []
        if not User.objects.filter(email='trainer1@gym.com').exists():
            trainer1 = User.objects.create_user(
                email='trainer1@gym.com',
                username='trainer1',
                password='Trainer@123',
                first_name='Mike',
                last_name='Trainer',
                role='trainer',
                gym_branch=branch1
            )
            trainers.append(trainer1)
        
        if not User.objects.filter(email='trainer2@gym.com').exists():
            trainer2 = User.objects.create_user(
                email='trainer2@gym.com',
                username='trainer2',
                password='Trainer@123',
                first_name='Sarah',
                last_name='Trainer',
                role='trainer',
                gym_branch=branch1
            )
            trainers.append(trainer2)
        
        if not User.objects.filter(email='trainer3@gym.com').exists():
            trainer3 = User.objects.create_user(
                email='trainer3@gym.com',
                username='trainer3',
                password='Trainer@123',
                first_name='Alex',
                last_name='Trainer',
                role='trainer',
                gym_branch=branch2
            )
            trainers.append(trainer3)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(trainers)} trainers'))
        
        # Create Members
        members = []
        if not User.objects.filter(email='member1@gym.com').exists():
            member1 = User.objects.create_user(
                email='member1@gym.com',
                username='member1',
                password='Member@123',
                first_name='Tom',
                last_name='Member',
                role='member',
                gym_branch=branch1
            )
            members.append(member1)
        
        if not User.objects.filter(email='member2@gym.com').exists():
            member2 = User.objects.create_user(
                email='member2@gym.com',
                username='member2',
                password='Member@123',
                first_name='Emma',
                last_name='Member',
                role='member',
                gym_branch=branch1
            )
            members.append(member2)
        
        if not User.objects.filter(email='member3@gym.com').exists():
            member3 = User.objects.create_user(
                email='member3@gym.com',
                username='member3',
                password='Member@123',
                first_name='David',
                last_name='Member',
                role='member',
                gym_branch=branch2
            )
            members.append(member3)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(members)} members'))
        
        # Create Workout Plans
        if not WorkoutPlan.objects.filter(title='Full Body Workout').exists():
            trainer = User.objects.filter(email='trainer1@gym.com').first()
            if trainer:
                WorkoutPlan.objects.create(
                    title='Full Body Workout',
                    description='Complete full body workout routine for beginners',
                    created_by=trainer,
                    gym_branch=branch1
                )
        
        if not WorkoutPlan.objects.filter(title='Cardio Plan').exists():
            trainer = User.objects.filter(email='trainer1@gym.com').first()
            if trainer:
                WorkoutPlan.objects.create(
                    title='Cardio Plan',
                    description='High intensity cardio training program',
                    created_by=trainer,
                    gym_branch=branch1
                )
        
        self.stdout.write(self.style.SUCCESS('✓ Created workout plans'))
        
        # Create Workout Tasks
        plans = WorkoutPlan.objects.all()
        members_branch1 = User.objects.filter(role='member', gym_branch=branch1)
        
        for plan in plans[:2]:
            for member in members_branch1[:1]:
                if not WorkoutTask.objects.filter(
                    workout_plan=plan,
                    member=member
                ).exists():
                    WorkoutTask.objects.create(
                        workout_plan=plan,
                        member=member,
                        status='pending',
                        due_date=datetime.now() + timedelta(days=7),
                        created_by=plan.created_by
                    )
        
        self.stdout.write(self.style.SUCCESS('✓ Created workout tasks'))
        
        self.stdout.write(self.style.SUCCESS(
            '\n✓ Test data created successfully!\n'
            '\nTest User Credentials:\n'
            '1. Super Admin: superadmin@gym.com / SuperAdmin@123\n'
            '2. Gym Manager (Downtown): manager1@gym.com / Manager@123\n'
            '3. Gym Manager (Uptown): manager2@gym.com / Manager@123\n'
            '4. Trainer (Downtown): trainer1@gym.com / Trainer@123\n'
            '5. Trainer (Downtown): trainer2@gym.com / Trainer@123\n'
            '6. Trainer (Uptown): trainer3@gym.com / Trainer@123\n'
            '7. Member (Downtown): member1@gym.com / Member@123\n'
            '8. Member (Downtown): member2@gym.com / Member@123\n'
            '9. Member (Uptown): member3@gym.com / Member@123\n'
        ))
