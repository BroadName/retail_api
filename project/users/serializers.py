from cProfile import label

from django_filters.utils import verbose_field_name
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from .models import CustomUser, Contact


class CreateCustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','email', 'first_name', 'last_name', 'type', 'password']


class UpdateCustomUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, help_text='При смене email необходимо подтвердить аккаунт')
    password = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'type', 'password']


class CreateContactSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Contact
        fields = ['id', 'city', 'street', 'house', 'structure', 'building',
                  'apartment', 'user', 'phone', 'additional_desc']


class UpdateContactSerializer(serializers.ModelSerializer):
    city = serializers.CharField(required=False, label='Город')
    street = serializers.CharField(required=False, label='Улица')
    phone = serializers.CharField(required=False, label='Телефон')
    user = serializers.HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Contact
        fields = ['id', 'city', 'street', 'house', 'structure', 'building',
                  'apartment', 'user', 'phone', 'additional_desc']


class GetContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'city', 'street', 'house', 'structure', 'building',
                  'apartment', 'phone', 'additional_desc', 'user']