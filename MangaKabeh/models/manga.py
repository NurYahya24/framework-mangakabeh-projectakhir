from django.db import models
from django.contrib.auth.models import User
import os

def manga_image_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = f"cover{ext}"
    sanitized_title = instance.title.replace(' ', '_').lower()
    sanitized_seller = instance.seller.id
    return f'manga/{sanitized_seller}/{sanitized_title}/{filename}'

class Manga(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField()
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=manga_image_upload_path)
    genre = models.ManyToManyField("Genre")
    class Meta :
        unique_together = ('title', 'seller')
    def __str__(self) -> str:
        return self.title
    
class VolumeManga(models.Model):
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE)
    volume = models.CharField(max_length=128, default='1')
    price = models.IntegerField()
    stock = models.IntegerField()
    
    def __str__(self) -> str:
        return f"{self.manga.title} - Volume {self.volume}"
    
    def update_stock(self, quantity):
        """Update the stock after an order."""
        self.stock -= quantity
        self.save()

    def restock(self, quantity):
        """Restock the volume (e.g., when an order is canceled)."""
        self.stock += quantity
        self.save()
    
class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name