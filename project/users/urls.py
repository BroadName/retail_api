from django.urls import path


from .views import (CreateCustomUserViewSet, CreateContactView, UpdateCustomUserViewSet, GetContactView, ConfirmEmailView,
                    UpdateContactView, DeleteContactView)

app_name = 'users'

urlpatterns = [
    path('registration/', CreateCustomUserViewSet.as_view(), name='registration'),
    path('add_contact/', CreateContactView.as_view(), name='add_contact'),
    path('update_user/', UpdateCustomUserViewSet.as_view(), name='update_user'),
    path('contacts/', GetContactView.as_view(), name='contacts'),
    path('confirm_email/<str:token>/<str:email>/', ConfirmEmailView.as_view(), name='confirm_email'),
    path('update_contact/<int:pk>/', UpdateContactView.as_view(), name='update_contact'),
    path('delete_contact/<int:pk>/', DeleteContactView.as_view(), name='delete_contact'),
]
