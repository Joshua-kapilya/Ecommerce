from django.conf import settings
from django.db import models

class Userprofile(models.Model):
    PROVINCES = [
        ('Central', 'Central'),
        ('Copperbelt', 'Copperbelt'),
        ('Eastern', 'Eastern'),
        ('Luapula', 'Luapula'),
        ('Lusaka', 'Lusaka'),
        ('Muchinga', 'Muchinga'),
        ('Northern', 'Northern'),
        ('North-Western', 'North-Western'),
        ('Southern', 'Southern'),
        ('Western', 'Western'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='userprofile',
        on_delete=models.CASCADE
    )
    is_vendor = models.BooleanField(default=False)

    # ✅ New fields
    mobile_number = models.CharField(max_length=20, blank=True)
    province = models.CharField(max_length=50, choices=PROVINCES, blank=True)
    city = models.CharField(max_length=100, blank=True)

    # ✅ Avatar and bio
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    bio = models.TextField(blank=True)
    is_verified=models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

