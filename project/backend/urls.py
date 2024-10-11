from django.urls import path
from .views import UploadProductsView, ListProductView, AddOrderItemView

app_name = 'backend'

urlpatterns = [
    path('upload/', UploadProductsView.as_view(), name='upload'),
    path('products/', ListProductView.as_view(), name='products'),
    path('add_order_items/', AddOrderItemView.as_view(), name='add_order_items'),
]