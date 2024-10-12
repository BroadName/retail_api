from rest_framework import serializers

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
    class Meta:
        model = Contact
        fields = ['id', 'city', 'street', 'house', 'structure', 'building',
                  'apartment', 'user', 'phone', 'additional_desc']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context.get('user')
        self.fields['user'].queryset = CustomUser.objects.filter(id=user.id)


class GetContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'city', 'street', 'house', 'structure', 'building',
                  'apartment', 'phone', 'additional_desc', 'user']