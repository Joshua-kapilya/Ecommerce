from django.db import models

# Create your models here.
class CarouselImage(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='carousel/')
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title
