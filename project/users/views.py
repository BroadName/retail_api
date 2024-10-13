from django.conf import settings
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import CustomUser, Contact, ConfirmToken
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
        token = ConfirmToken.objects.create(user=user)

        link = f'http://127.0.0.1:8000/api/v1/confirm_email/{token.token}/{user.email}'
        body = f"""
                Please confirm your email by clicking on the link:
                <a href="{link}">Confirm your email</a>
                """
        msg = EmailMessage('Registration on retail site',
                           body, settings.EMAIL_HOST_USER, [user.email])
        msg.content_subtype = "html"
        msg.send()
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


class ConfirmEmailView(ListAPIView):
    def get(self, request, *args, **kwargs):
        token = self.kwargs.get('token')
        email = self.kwargs.get('email')
        if token and email:
            confirm_token = ConfirmToken.objects.get(token=token, user__email = email)
            if confirm_token:
                confirm_token.user.is_active = True
                confirm_token.user.save()
                confirm_token.delete()
                return Response({"Success": "Email confirmed successfully"}, status=status.HTTP_201_CREATED)
            return Response({"Error": "Invalid token or email"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"Error": "Token and email are required"}, status=status.HTTP_403_FORBIDDEN)