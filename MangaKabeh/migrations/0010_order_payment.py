# Generated by Django 5.1.1 on 2024-11-28 16:17

import MangaKabeh.models.order
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MangaKabeh', '0009_order_status_alter_order_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.ImageField(blank=True, upload_to=MangaKabeh.models.order.upload_payment),
        ),
    ]
