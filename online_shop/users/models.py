from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    groups = models.ManyToManyField(
    'auth.Group',
    verbose_name='groups',
    blank=True,
    help_text='The groups this user belongs to...',
    related_name="custom_user_set",
    related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user...',
        related_name="custom_user_set",
        related_query_name="user",
    )

    profile_pic = models.ImageField(upload_to='profile_pictures', blank=True, null=True)
    phone_number = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'users'
        verbose_name_plural = 'users'

    
    def __str__(self):
        return self.username