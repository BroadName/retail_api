from django.urls import path
from .views import UploadProductsView

app_name = 'backend'

urlpatterns = [
    path('upload/', UploadProductsView.as_view(), name='upload'),
]