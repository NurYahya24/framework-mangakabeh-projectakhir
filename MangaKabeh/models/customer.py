from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Customer(models.Model):
    email = models.EmailField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=13, unique=True)
    username = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    
    def __str__(self) -> str:
        return self.username
    
@receiver(post_save, sender=Customer)
def create_user_for_customer(sender, instance, created, **kwargs):
    if created:
        user = User.objects.create_user(
            username = instance.username,
            email= instance.email,
            password= instance.password,
            
        )
        customer_group, created = Group.objects.get_or_create(name='Customer')
        user.groups.add(customer_group)