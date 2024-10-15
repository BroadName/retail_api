from rest_framework.permissions import BasePermission


class IsOwnerOrderItem(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.order.user


class IsOwnerOrder(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user