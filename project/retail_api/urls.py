from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('users.urls')),
    path('api/v1/', include('backend.urls', namespace='backend')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
