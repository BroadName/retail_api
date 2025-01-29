from django.core.cache import cache
from .tasks import send_email
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .permissions import IsOwnerOrReadOnly
from .models import CustomUser, Contact, ConfirmToken
from .serializers import (CreateCustomUserSerializer, CreateContactSerializer, UpdateCustomUserSerializer,
                          GetContactSerializer, UpdateContactSerializer)
import logging


logger = logging.getLogger(__name__)


class CreateCustomUserViewSet(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CreateCustomUserSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['email', 'first_name', 'last_name']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.create_user(**serializer.validated_data)
        token = ConfirmToken.objects.create(user=user)
        cache.set(f'user_email_{user.id}', user.email, timeout=300)
        cache.set(f'token_{user.id}', token.token, timeout=300)
        send_email.delay(user.email, token.token, [user.email])
        return JsonResponse({"Success": "Account created successfully. The message will be sent soon, please confirm your email"},
                            status=status.HTTP_201_CREATED)


class UpdateCustomUserViewSet(UpdateAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = CustomUser.objects.all()
    serializer_class = UpdateCustomUserSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.get(id=self.request.user.id)
        if serializer.validated_data.get('password') is not None:
            user.set_password(serializer.validated_data.get('password', user.password))
        if (serializer.validated_data.get('email') is not None and
                request.user.email != serializer.validated_data.get('email')):
            email = serializer.validated_data.get('email')
            token = ConfirmToken.objects.create(user=user)
            task = send_email.delay(email, token.token, [email])
            cache.set(f'user_email_{user.id}', email, timeout=300)
            cache.set(f'token_{user.id}', token, timeout=300)
            logger.info(f"Email verification task started for user {user.id} with email {email}")

        user.first_name = serializer.validated_data.get('first_name', user.first_name)
        user.last_name = serializer.validated_data.get('last_name', user.last_name)
        user.type = serializer.validated_data.get('type', user.type)
        user.save()
        return Response({"Process ID": task.id,
                         "Processing": "We send a confirmation message to your email, it will be valid for 5 minutes"},
                        status=status.HTTP_201_CREATED)


class CreateContactView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Contact.objects.all()
    serializer_class = CreateContactSerializer


class GetContactView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Contact.objects.all()
    serializer_class = GetContactSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class UpdateContactView(UpdateAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Contact.objects.all()
    serializer_class = UpdateContactSerializer


class DeleteContactView(DestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Contact.objects.all()
    serializer_class = GetContactSerializer


class ConfirmEmailView(ListAPIView):
    def get(self, request, *args, **kwargs):
        token = self.kwargs.get('token')
        email = self.kwargs.get('email')
        if token and email:
            confirm_token = ConfirmToken.objects.get(token=token, user__email = email)
            if confirm_token:
                confirm_token.user.is_active = True
                confirm_token.user.email = email
                confirm_token.user.save()
                confirm_token.delete()
                return Response({"Success": "Email confirmed successfully"}, status=status.HTTP_201_CREATED)
            return Response({"Error": "Invalid token or email"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"Error": "Token and email are required"}, status=status.HTTP_403_FORBIDDEN)