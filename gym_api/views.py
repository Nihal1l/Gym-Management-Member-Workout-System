from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import User, GymBranch, WorkoutPlan, WorkoutTask, ActivityLog
from .serializers import (
    UserSerializer, UserDetailSerializer, UserCreateSerializer,
    GymBranchSerializer, WorkoutPlanSerializer, WorkoutTaskSerializer,
    WorkoutTaskUpdateSerializer, ActivityLogSerializer, LoginSerializer,
    TokenSerializer, RefreshTokenSerializer
)
from .permissions import (
    IsSuperAdmin, IsGymManager, IsTrainer, IsMember,
    IsSameBranch, IsGymManagerOrSuperAdmin, IsOwnerOrGymManager,
    CanEditOwnTask
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """User login endpoint"""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = serializer.validated_data['user']
    refresh = RefreshToken.for_user(user)
    
    # Log the login activity
    ActivityLog.objects.create(
        user=user,
        action='login',
        model_name='User',
        object_id=str(user.id)
    )
    
    response_data = {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserDetailSerializer(user).data
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """Refresh token endpoint"""
    serializer = RefreshTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    try:
        refresh = RefreshToken(serializer.validated_data['refresh'])
        response_data = {
            'access': str(refresh.access_token),
        }
        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': 'Invalid refresh token'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """Get current user profile"""
    serializer = UserDetailSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


class GymBranchViewSet(viewsets.ModelViewSet):
    """
    Gym Branch ViewSet
    - Super Admin: Can create, list, retrieve, update, delete all branches
    - Other roles: Can only list and retrieve their assigned branch
    """
    queryset = GymBranch.objects.all()
    serializer_class = GymBranchSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'location']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if self.request.user.role == 'super_admin':
            return GymBranch.objects.all()
        elif self.request.user.gym_branch:
            return GymBranch.objects.filter(id=self.request.user.gym_branch.id)
        return GymBranch.objects.none()
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsSuperAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        if request.user.role != 'super_admin':
            return Response(
                {'error': 'Only super admin can create gym branches'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)


class UserViewSet(viewsets.ModelViewSet):
    """
    User ViewSet
    - Super Admin: Can manage all users
    - Gym Manager: Can create trainers and members for their branch, view users in their branch
    - Others: Can view their own profile
    """
    queryset = User.objects.all()
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'gym_branch']
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'email']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'super_admin':
            return User.objects.all()
        elif user.role == 'gym_manager':
            return User.objects.filter(gym_branch=user.gym_branch)
        else:
            # Members and trainers can only view their own profile
            return User.objects.filter(id=user.id)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        else:
            return UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsGymManagerOrSuperAdmin]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsSuperAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Enforce branch restrictions
        user_role = request.data.get('role')
        gym_branch = request.data.get('gym_branch')
        
        if request.user.role == 'gym_manager':
            if user_role == 'super_admin':
                return Response(
                    {'error': 'Manager cannot create super admin users'},
                    status=status.HTTP_403_FORBIDDEN
                )
            if user_role not in ['trainer', 'member']:
                return Response(
                    {'error': 'Manager can only create trainers and members'},
                    status=status.HTTP_403_FORBIDDEN
                )
            if gym_branch != request.user.gym_branch.id:
                return Response(
                    {'error': 'Manager can only create users for their own branch'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=False, methods=['get'])
    def trainers(self, request):
        """Get all trainers in the branch"""
        if request.user.role == 'super_admin':
            trainers = User.objects.filter(role='trainer')
        elif request.user.role == 'gym_manager':
            trainers = User.objects.filter(role='trainer', gym_branch=request.user.gym_branch)
        else:
            return Response(
                {'error': 'You do not have permission to view trainers'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserSerializer(trainers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def members(self, request):
        """Get all members in the branch"""
        if request.user.role == 'super_admin':
            members = User.objects.filter(role='member')
        elif request.user.role == 'gym_manager':
            members = User.objects.filter(role='member', gym_branch=request.user.gym_branch)
        else:
            return Response(
                {'error': 'You do not have permission to view members'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserSerializer(members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WorkoutPlanViewSet(viewsets.ModelViewSet):
    """
    Workout Plan ViewSet
    - Trainer: Can create plans for their branch
    - Gym Manager: Can view all plans in their branch
    - Super Admin: Can view all plans
    """
    queryset = WorkoutPlan.objects.all()
    serializer_class = WorkoutPlanSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['gym_branch', 'created_by']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'super_admin':
            return WorkoutPlan.objects.all()
        elif user.role in ['gym_manager', 'trainer']:
            return WorkoutPlan.objects.filter(gym_branch=user.gym_branch)
        else:
            # Members cannot view workout plans directly
            return WorkoutPlan.objects.none()
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsTrainer]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsTrainer]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        if request.user.role != 'trainer':
            return Response(
                {'error': 'Only trainers can create workout plans'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.created_by != request.user:
            return Response(
                {'error': 'You can only update your own workout plans'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.created_by != request.user:
            return Response(
                {'error': 'You can only delete your own workout plans'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class WorkoutTaskViewSet(viewsets.ModelViewSet):
    """
    Workout Task ViewSet
    - Trainer: Can create, assign, and update tasks in their branch
    - Member: Can view and update their own tasks
    - Manager: Can view all tasks in their branch
    """
    queryset = WorkoutTask.objects.all()
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'member', 'workout_plan']
    search_fields = ['member__email', 'workout_plan__title']
    ordering_fields = ['created_at', 'due_date', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'super_admin':
            return WorkoutTask.objects.all()
        elif user.role == 'gym_manager':
            return WorkoutTask.objects.filter(workout_plan__gym_branch=user.gym_branch)
        elif user.role == 'trainer':
            return WorkoutTask.objects.filter(workout_plan__gym_branch=user.gym_branch)
        elif user.role == 'member':
            # Members can only view their own tasks
            return WorkoutTask.objects.filter(member=user)
        return WorkoutTask.objects.none()
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return WorkoutTaskUpdateSerializer
        return WorkoutTaskSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsTrainer]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated]
        elif self.action == 'destroy':
            permission_classes = [IsTrainer]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        if request.user.role != 'trainer':
            return Response(
                {'error': 'Only trainers can assign workout tasks'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate that trainer is assigning to member from same branch
        member_id = request.data.get('member')
        workout_plan_id = request.data.get('workout_plan')
        
        if member_id and workout_plan_id:
            try:
                member = User.objects.get(id=member_id)
                workout_plan = WorkoutPlan.objects.get(id=workout_plan_id)
                
                if member.gym_branch != request.user.gym_branch:
                    return Response(
                        {'error': 'Cannot assign task to member from different branch'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                if workout_plan.gym_branch != request.user.gym_branch:
                    return Response(
                        {'error': 'Cannot assign task from different branch'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except (User.DoesNotExist, WorkoutPlan.DoesNotExist):
                pass
        
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Members can only update status
        if request.user.role == 'member':
            if instance.member != request.user:
                return Response(
                    {'error': 'You can only update your own tasks'},
                    status=status.HTTP_403_FORBIDDEN
                )
            # Member can only update status
            allowed_fields = ['status']
            for field in request.data.keys():
                if field not in allowed_fields:
                    return Response(
                        {'error': f'You can only update status'},
                        status=status.HTTP_403_FORBIDDEN
                    )
        
        # Trainers can update tasks in their branch
        elif request.user.role == 'trainer':
            if instance.workout_plan.gym_branch != request.user.gym_branch:
                return Response(
                    {'error': 'You can only update tasks from your branch'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if request.user.role == 'trainer':
            if instance.created_by != request.user:
                return Response(
                    {'error': 'You can only delete tasks you created'},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            return Response(
                {'error': 'Only trainers can delete tasks'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Activity log view set for audit trail"""
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['user', 'action', 'model_name']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


@api_view(['GET'])
@permission_classes([AllowAny])
def welcome_view(request):
    """Welcome endpoint for API root"""
    return Response({
        'message': 'Welcome to Gym Management API',
        'description': 'For ongoing use, you have to log in first',
        'endpoints': {
            'login': '/api/v1/auth/login/',
            'refresh_token': '/api/v1/auth/refresh/',
            'profile': '/api/v1/auth/profile/',
            'gym_branches': '/api/v1/gym-branches/',
            'users': '/api/v1/users/',
            'workout_plans': '/api/v1/workout-plans/',
            'workout_tasks': '/api/v1/workout-tasks/',
            'activity_logs': '/api/v1/activity-logs/'
        },
        'test_credentials': {
            'super_admin': {
                'email': 'superadmin@gym.com',
                'password': 'SuperAdmin@123',
                'role': 'super_admin'
            },
            'gym_manager': {
                'email': 'manager1@gym.com',
                'password': 'Manager@123',
                'role': 'gym_manager'
            },
            'trainer': {
                'email': 'trainer1@gym.com',
                'password': 'Trainer@123',
                'role': 'trainer'
            },
            'member': {
                'email': 'member1@gym.com',
                'password': 'Member@123',
                'role': 'member'
            }
        },
        'documentation': {
            'readme': 'https://github.com/yourusername/gym-management-api/blob/main/README.md',
            'api_specification': 'https://github.com/yourusername/gym-management-api/blob/main/API_SPECIFICATION.md',
            'database_schema': 'https://github.com/yourusername/gym-management-api/blob/main/DATABASE_SCHEMA.md'
        }
    })
