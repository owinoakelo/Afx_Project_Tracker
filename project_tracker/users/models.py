import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    """
    Standard Django user model with OTP authentication.
    """
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
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
    # OTP fields
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    is_otp_verified = models.BooleanField(default=False)
    otp_method = models.CharField(
        max_length=10,
        choices=[('email', 'Email'), ('sms', 'SMS')],
        default='email',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uid=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

    def is_otp_valid(self):
        """Check if OTP is still valid."""
        if not self.otp_expiry:
            return False
        return timezone.now() < self.otp_expiry

    def set_otp(self, otp_code, validity_minutes=10):
        """Set OTP code and expiry time."""
        self.otp_code = otp_code
        self.otp_expiry = timezone.now() + timedelta(minutes=validity_minutes)
        self.save()
