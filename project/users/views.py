from django.conf import settings
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from .models import CustomUser, Contact
from .serializers import (CreateCustomUserSerializer, CreateContactSerializer, UpdateCustomUserSerializer,
                          GetContactSerializer)


class CustomUserViewSet(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CreateCustomUserSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['email', 'first_name', 'last_name']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.create_user(**serializer.validated_data)
        return JsonResponse({"Success": "Account created successfully, please confirm your email"},
                            status=status.HTTP_201_CREATED)


class UpdateCustomUserViewSet(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()
    serializer_class = UpdateCustomUserSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.get(id=self.request.user.id)
        if (serializer.validated_data.get('email') is not None and
                request.user.email != serializer.validated_data.get('email')):
            user.email = serializer.validated_data.get('email')
            user.is_active = False
        user.first_name = serializer.validated_data.get('first_name', user.first_name)
        user.last_name = serializer.validated_data.get('last_name', user.last_name)
        user.type = serializer.validated_data.get('type', user.type)
        if serializer.validated_data.get('password') is not None:
            user.set_password(serializer.validated_data.get('password', user.password))
        user.save()
        return JsonResponse({"Success": "Profile updated successfully"}, status=status.HTTP_201_CREATED)


class CreateContactView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Contact.objects.all()
    serializer_class = CreateContactSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context


class GetContactView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Contact.objects.all()
    serializer_class = GetContactSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)