from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):

        """
        Authenticate a user using their email and password.

        Parameters:
            request (django.http.request.HttpRequest): The request object.
            username (str): The email address of the user.
            password (str): The password of the user.
            **kwargs: Additional keyword arguments.

        Returns:
            django.contrib.auth.models.AbstractBaseUser: The authenticated user.
        """

        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None