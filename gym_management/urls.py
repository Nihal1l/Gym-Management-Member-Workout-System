"""
URL configuration for gym_management project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

@api_view(['GET'])
@permission_classes([AllowAny])
def root_welcome(request):
    """Root endpoint welcome message"""
    return Response({
        'name': 'Gym Management & Member Workout System',
        'version': '1.0.0',
        'message': 'Welcome to Gym Management API',
        'description': 'For ongoing use, you have to log in first',
        'api_endpoint': '/api/v1/',
        'admin_panel': '/admin/',
        'status': 'Online'
    })

urlpatterns = [
    path('', root_welcome, name='root'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('gym_api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
