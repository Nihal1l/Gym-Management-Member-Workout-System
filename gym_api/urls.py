from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'gym-branches', views.GymBranchViewSet, basename='gymbranch')
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'workout-plans', views.WorkoutPlanViewSet, basename='workoutplan')
router.register(r'workout-tasks', views.WorkoutTaskViewSet, basename='workoutask')
router.register(r'activity-logs', views.ActivityLogViewSet, basename='activitylog')

urlpatterns = [
    path('', views.welcome_view, name='welcome'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/refresh/', views.refresh_token_view, name='refresh_token'),
    path('auth/profile/', views.profile_view, name='profile'),
    path('', include(router.urls)),
]
