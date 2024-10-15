from django.urls import path
from .views import (UploadProductsView, ListProductView, AddOrderItemView, ListItemsOrder, DeleteOrderItemView,
                    ListOrderView, ConfirmOrderView, DetailOrderView)

app_name = 'backend'

urlpatterns = [
    path('upload/', UploadProductsView.as_view(), name='upload'),
    path('products/', ListProductView.as_view(), name='products'),
    path('add_order_items/', AddOrderItemView.as_view(), name='add_order_items'),
    path('basket', ListItemsOrder.as_view(), name='basket'),
    path('order/<int:pk>/', DetailOrderView.as_view(), name='order'),
    path('delete_order_item/<int:pk>/', DeleteOrderItemView.as_view(), name='delete_order_item'),
    path('orders/', ListOrderView.as_view(), name = 'orders'),
    path('confirm/<int:id>/', ConfirmOrderView.as_view(), name='confirm'),
]