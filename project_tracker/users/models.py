import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Standard Django user model with additional customization fields.
    """
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150, blank=False, null=False)
    # Override the inherited many-to-many relations to avoid reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='users_custom_set',
        blank=True,
        help_text=('The groups this user belongs to.'),
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='users_custom_permissions_set',
        blank=True,
        help_text=('Specific permissions for this user.'),
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uid=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email
