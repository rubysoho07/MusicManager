from __future__ import unicode_literals

from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager

from manager_core.models import Album
from django.conf import settings


class MmUserManager(BaseUserManager):
    """User manager class for MusicManager user."""

    def create_user(self, email, name, nickname, password):
        """
        Creates and saves a User with given information below

        :param email: E-mail address of a user.
        :param name: Real name of a user.
        :param nickname: Nickname of a user.
        :param password: Password of a user
        :return: user
        """

        if not email:
            raise ValueError('User must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            nickname=nickname,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **kwargs):
        user = self.model(
            email=self.normalize_email(email),
            is_admin=True,
            is_superuser=True,
            **kwargs
        )
        user.set_password(password)
        user.save()
        return user


class MmUser(AbstractBaseUser, PermissionsMixin):
    """Model for a MusicManager user."""

    email = models.EmailField(max_length=255, verbose_name='E-mail address', unique=True)
    name = models.CharField(max_length=255, null=False)
    nickname = models.CharField(max_length=255, null=False, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    albums = models.ManyToManyField(Album, through='MmUserAlbum')

    objects = MmUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'nickname']

    def get_full_name(self):
        """Return the user's nickname."""

        return self.nickname

    def get_short_name(self):
        """Return the user's nickname."""

        return self.nickname

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """
        Does the user have a specific permission?
        :return: True
        """

        return True

    def has_module_perms(self, app_label):
        """
        Does the user have permissions to view the app `app_label`?
        :param app_label:
        :return: True
        """

        return True

    @property
    def is_staff(self):
        """ Is the user a member or staff? """

        return self.is_admin


class MmUserAlbum(models.Model):
    """Album of an MusicManager user."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    add_time = models.DateTimeField(auto_now_add=True)
    score = models.PositiveSmallIntegerField(null=True, default=None)

    class Meta:
        ordering = ['-add_time']

