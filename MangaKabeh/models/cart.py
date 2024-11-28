
from django.db import models
from .manga import VolumeManga
from django.contrib.auth.models import User

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart,related_name="cart_items", on_delete=models.CASCADE)
    volume = models.ForeignKey(VolumeManga, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    
    @property
    def total_price(self):
        return self.quantity * self.volume.price

    def __str__(self):
        return f"{self.volume} (x{self.quantity}) from {self.seller}"
