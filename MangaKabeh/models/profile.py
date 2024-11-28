from django.db import models
from django.contrib.auth.models import User
import os

def user_profile_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = f"{instance.user.username}{ext}"
    return os.path.join('profile', filename)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    picture = models.ImageField(upload_to=user_profile_upload_path)