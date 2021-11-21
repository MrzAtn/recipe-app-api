from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,\
                                        PermissionsMixin

# Create your models here.

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **kwargs):
        """Create and save a new user"""
        # user = self.model(email=email, **kwargs) # Not normalized
        if not email:
            raise ValueError("Email must have a value in order to create a User.")
        user = self.model(email=self.normalize_email(email), **kwargs) # Normalized
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_superuser = True # attr given by the PermissionsMixins class
        user.is_staff = True
        user.save()
        return user 


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    # by default it's settle to username but we force it to email
    USERNAME_FIELD = 'email'