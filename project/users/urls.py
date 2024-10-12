from django.urls import path


from .views import CustomUserViewSet, CreateContactView, UpdateCustomUserViewSet, GetContactView

app_name = 'users'

urlpatterns = [
    path('users/', CustomUserViewSet.as_view(), name='users'),
    path('add_contact/', CreateContactView.as_view(), name='add_contact'),
    path('update_user/<int:pk>/', UpdateCustomUserViewSet.as_view(), name='update_user'),
    path('contacts/', GetContactView.as_view(), name='contacts'),
]
