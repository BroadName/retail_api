from django.urls import path
from .views import UploadProductsView, ListProductView

app_name = 'backend'

urlpatterns = [
    path('upload/', UploadProductsView.as_view(), name='upload'),
    path('products/', ListProductView.as_view(), name='products'),
]