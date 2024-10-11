from django.urls import path


from .views import CustomUserViewSet, CreateContactView

app_name = 'users'

urlpatterns = [
    path('users/', CustomUserViewSet.as_view(), name='users'),
    path('add_contact/', CreateContactView.as_view(), name='add_contact'),
]
