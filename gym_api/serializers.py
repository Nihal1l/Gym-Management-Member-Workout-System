from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, GymBranch, WorkoutPlan, WorkoutTask, ActivityLog
from django.core.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer"""
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'gym_branch', 'is_active', 'created_at']
        read_only_fields = ['created_at', 'id']


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer with gym branch info"""
    gym_branch_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'gym_branch', 'gym_branch_detail', 'is_active', 'created_at']
        read_only_fields = ['created_at', 'id']
    
    def get_gym_branch_detail(self, obj):
        if obj.gym_branch:
            return {
                'id': obj.gym_branch.id,
                'name': obj.gym_branch.name,
                'location': obj.gym_branch.location
            }
        return None


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password_confirm', 'role', 'gym_branch']
    
    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError("Passwords do not match")
        
        # Role-specific validations
        role = data.get('role')
        gym_branch = data.get('gym_branch')
        
        if role == 'super_admin':
            if gym_branch:
                raise serializers.ValidationError("Super admin should not have a gym branch assigned")
        else:
            if not gym_branch:
                raise serializers.ValidationError("Non-admin users must have a gym branch")
        
        # Check 3 trainers limit per branch
        if role == 'trainer' and gym_branch:
            trainer_count = User.objects.filter(
                role='trainer',
                gym_branch=gym_branch
            ).count()
            if trainer_count >= 3:
                raise serializers.ValidationError("Maximum 3 trainers allowed per gym branch")
        
        return data
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        # Generate unique username from email
        email = validated_data['email']
        username = email.split('@')[0]
        counter = 1
        original_username = username
        # Ensure username is unique
        while User.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1
        validated_data['username'] = username
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class GymBranchSerializer(serializers.ModelSerializer):
    """Gym branch serializer"""
    trainer_count = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = GymBranch
        fields = ['id', 'name', 'location', 'is_active', 'trainer_count', 'member_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'id']
    
    def get_trainer_count(self, obj):
        return User.objects.filter(role='trainer', gym_branch=obj).count()
    
    def get_member_count(self, obj):
        return User.objects.filter(role='member', gym_branch=obj).count()


class WorkoutPlanSerializer(serializers.ModelSerializer):
    """Workout plan serializer"""
    created_by_detail = UserSerializer(source='created_by', read_only=True)
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkoutPlan
        fields = ['id', 'title', 'description', 'created_by', 'created_by_detail', 'gym_branch', 'task_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'id', 'created_by']
    
    def get_task_count(self, obj):
        return obj.tasks.count()
    
    def validate(self, data):
        """Ensure trainer can only create plans for their own branch and prevent duplicates"""
        user = self.context['request'].user
        
        # If gym_branch is provided by the user, validate it matches their branch
        if 'gym_branch' in data and user.role == 'trainer':
            requested_branch = data.get('gym_branch')
            if requested_branch != user.gym_branch:
                raise serializers.ValidationError(
                    "Trainer can only create workout plans for their own gym branch"
                )
        
        # Check for duplicate workout plan (same title in same branch)
        title = data.get('title')
        gym_branch = data.get('gym_branch') or user.gym_branch
        
        duplicate_exists = WorkoutPlan.objects.filter(
            title__iexact=title,
            gym_branch=gym_branch
        ).exists()
        
        if duplicate_exists:
            raise serializers.ValidationError(
                f"A workout plan with the title '{title}' already exists in this gym branch"
            )
        
        return data
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['gym_branch'] = self.context['request'].user.gym_branch
        return super().create(validated_data)


class WorkoutTaskSerializer(serializers.ModelSerializer):
    """Workout task serializer"""
    member_detail = UserSerializer(source='member', read_only=True)
    created_by_detail = UserSerializer(source='created_by', read_only=True)
    workout_plan_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkoutTask
        fields = ['id', 'workout_plan', 'workout_plan_detail', 'member', 'member_detail', 
                  'status', 'due_date', 'created_by', 'created_by_detail', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'id', 'created_by']
    
    def get_workout_plan_detail(self, obj):
        return {
            'id': obj.workout_plan.id,
            'title': obj.workout_plan.title,
            'description': obj.workout_plan.description
        }
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate(self, data):
        # Ensure member and workout plan are from same branch
        member = data.get('member')
        workout_plan = data.get('workout_plan')
        
        if member and workout_plan:
            if member.gym_branch != workout_plan.gym_branch:
                raise serializers.ValidationError("Member must be from the same gym branch as the workout plan")
        
        return data


class WorkoutTaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating task status"""
    class Meta:
        model = WorkoutTask
        fields = ['status']


class ActivityLogSerializer(serializers.ModelSerializer):
    """Activity log serializer"""
    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'action', 'model_name', 'object_id', 'changes', 'created_at']
        read_only_fields = ['id', 'created_at']


class LoginSerializer(serializers.Serializer):
    """Login serializer"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")
        
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password")
        
        if not user.is_active:
            raise serializers.ValidationError("User account is inactive")
        
        data['user'] = user
        return data


class TokenSerializer(serializers.Serializer):
    """Token serializer"""
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = UserDetailSerializer(read_only=True)


class RefreshTokenSerializer(serializers.Serializer):
    """Refresh token serializer"""
    refresh = serializers.CharField()
    access = serializers.CharField(read_only=True)
