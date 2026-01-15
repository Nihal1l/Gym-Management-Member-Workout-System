from django.contrib import admin
from .models import User, GymBranch, WorkoutPlan, WorkoutTask, ActivityLog


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'gym_branch', 'is_active', 'created_at']
    list_filter = ['role', 'gym_branch', 'is_active', 'created_at']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(GymBranch)
class GymBranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'location']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'gym_branch', 'created_at']
    list_filter = ['gym_branch', 'created_by', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(WorkoutTask)
class WorkoutTaskAdmin(admin.ModelAdmin):
    list_display = ['workout_plan', 'member', 'status', 'due_date', 'created_at']
    list_filter = ['status', 'created_by', 'created_at', 'due_date']
    search_fields = ['member__email', 'workout_plan__title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'created_at']
    list_filter = ['action', 'model_name', 'created_at']
    search_fields = ['user__email', 'object_id']
    readonly_fields = ['created_at']
