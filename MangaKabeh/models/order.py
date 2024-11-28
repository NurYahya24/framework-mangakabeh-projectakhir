from django.db import models
from django.contrib.auth.models import User
from .manga import VolumeManga


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=(
        ('Pending', 'Pending'),
        ('On Process', 'On Process'),
        ('Done', 'Done'),
        ('Canceled', 'Canceled'),
    ))
    created_at = models.DateTimeField(auto_now_add=True)
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    volume = models.ForeignKey(VolumeManga, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
