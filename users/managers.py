from django.contrib.auth.models import UserManager


class CustomUserManager(UserManager):

    def create_user(self, username, email=None, password=None, **extra_fields):
        if not email:
            raise ValueError('The email must be set')

        return super().create_user(username, email, password, **extra_fields)
