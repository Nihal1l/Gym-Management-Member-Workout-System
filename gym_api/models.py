from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Custom User model with role-based access"""
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('gym_manager', 'Gym Manager'),
        ('trainer', 'Trainer'),
        ('member', 'Member'),
    )
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    gym_branch = models.ForeignKey(
        'GymBranch', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='users'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['gym_branch']),
        ]


class GymBranch(models.Model):
    """Gym branch/location"""
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.location}"
    
    class Meta:
        verbose_name = 'Gym Branch'
        verbose_name_plural = 'Gym Branches'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]


class WorkoutPlan(models.Model):
    """Workout plan created by trainers"""
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_workout_plans',
        limit_choices_to={'role': 'trainer'}
    )
    gym_branch = models.ForeignKey(
        GymBranch,
        on_delete=models.CASCADE,
        related_name='workout_plans'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.created_by.email}"
    
    def clean(self):
        if self.created_by.role != 'trainer':
            raise ValidationError("Workout plan can only be created by trainers")
        if self.created_by.gym_branch != self.gym_branch:
            raise ValidationError("Trainer can only create plans for their own gym branch")
    
    class Meta:
        verbose_name = 'Workout Plan'
        verbose_name_plural = 'Workout Plans'
        indexes = [
            models.Index(fields=['gym_branch', 'created_by']),
            models.Index(fields=['created_at']),
        ]


class WorkoutTask(models.Model):
    """Task assigned to members from workout plans"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )
    
    workout_plan = models.ForeignKey(
        WorkoutPlan,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        limit_choices_to={'role': 'member'}
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    due_date = models.DateTimeField()
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_workout_tasks',
        limit_choices_to={'role': 'trainer'}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.workout_plan.title} - {self.member.email} ({self.status})"
    
    def clean(self):
        if self.member.role != 'member':
            raise ValidationError("Task can only be assigned to members")
        if self.created_by and self.created_by.role != 'trainer':
            raise ValidationError("Task can only be created by trainers")
        if self.workout_plan.gym_branch != self.member.gym_branch:
            raise ValidationError("Cannot assign task to member from different branch")
        if self.created_by and self.created_by.gym_branch != self.workout_plan.gym_branch:
            raise ValidationError("Trainer must be from the same gym branch")
    
    class Meta:
        verbose_name = 'Workout Task'
        verbose_name_plural = 'Workout Tasks'
        indexes = [
            models.Index(fields=['member', 'status']),
            models.Index(fields=['workout_plan', 'member']),
            models.Index(fields=['created_at']),
            models.Index(fields=['due_date']),
        ]


class ActivityLog(models.Model):
    """Activity log for audit trail"""
    ACTION_CHOICES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    changes = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.model_name}"
    
    class Meta:
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['created_at']),
        ]
