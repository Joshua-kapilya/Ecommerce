from django.conf import settings
from django.db import models
import requests

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

    mobile_number = models.CharField(max_length=20, blank=True)
    province = models.CharField(max_length=50, choices=PROVINCES, blank=True)
    city = models.CharField(max_length=100, blank=True)

    # Avatar and bio
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)

    # ✅ Latitude and Longitude
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    # ✅ Automatically get coordinates when saving
    def save(self, *args, **kwargs):
        if self.city or self.province:
            self.latitude, self.longitude = self.get_coordinates(f"{self.city}, {self.province}, Zambia")
        super().save(*args, **kwargs)

    def get_coordinates(self, address):
        """Return (latitude, longitude) from an address using Google Maps API"""
        if not hasattr(settings, 'GOOGLE_MAPS_API_KEY'):
            return None, None
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={settings.GOOGLE_MAPS_API_KEY}"
        response = requests.get(url).json()
        if response.get("results"):
            location = response["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
        return None, None
