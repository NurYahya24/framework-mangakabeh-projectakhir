from django.db import models
from .seller import Seller


def manga_image_upload_path(instance, filename):
    sanitized_title = instance.title.replace(' ', '_').lower()
    sanitized_seller = instance.seller.username.replace(' ', '_').lower()
    return f'manga/{sanitized_seller}/{sanitized_title}/{filename}'

class Manga(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField()
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=manga_image_upload_path)
    genre = models.ManyToManyField("Genre")
    def __str__(self) -> str:
        return self.title
    
class VolumeManga(models.Model):
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE)
    volume = models.CharField(max_length=128, default='1')
    price = models.IntegerField()
    
    def __str__(self) -> str:
        return self.volume
    
class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name