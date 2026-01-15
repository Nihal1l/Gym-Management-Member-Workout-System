from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):
    """All authenticated users can access"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsSuperAdmin(BasePermission):
    """Only super admin can access"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'super_admin')


class IsGymManager(BasePermission):
    """Only gym manager can access"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'gym_manager')


class IsTrainer(BasePermission):
    """Only trainer can access"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'trainer')


class IsMember(BasePermission):
    """Only member can access"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'member')


class IsSameBranch(BasePermission):
    """Users can only access data from their branch"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Super admin can access all branches
        if request.user.role == 'super_admin':
            return True
        
        # Other roles need to have a gym_branch
        return request.user.gym_branch is not None
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'super_admin':
            return True
        
        # Get the gym_branch from the object
        if hasattr(obj, 'gym_branch'):
            return obj.gym_branch == request.user.gym_branch
        
        if hasattr(obj, 'user'):
            return obj.user.gym_branch == request.user.gym_branch
        
        if isinstance(obj, type) and hasattr(obj, 'gym_branch'):
            return obj.gym_branch == request.user.gym_branch
        
        return False


class IsGymManagerOrSuperAdmin(BasePermission):
    """Only gym manager or super admin can access"""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['gym_manager', 'super_admin']
        )


class IsTrainerOrManager(BasePermission):
    """Only trainer or gym manager can access"""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['trainer', 'gym_manager']
        )


class IsOwnerOrGymManager(BasePermission):
    """User can only access their own data or manager can access their branch users"""
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'super_admin':
            return True
        
        if request.user.role == 'gym_manager':
            # Manager can access users from their branch
            return obj.gym_branch == request.user.gym_branch
        
        # Other roles can only access their own data
        return obj == request.user


class CanEditOwnTask(BasePermission):
    """Member can update their own tasks, trainer can update any task in their branch"""
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'super_admin':
            return True
        
        if request.user.role == 'trainer':
            # Trainer can update tasks in their branch
            return obj.workout_plan.gym_branch == request.user.gym_branch
        
        if request.user.role == 'member':
            # Member can only update their own tasks
            return obj.member == request.user
        
        return False
