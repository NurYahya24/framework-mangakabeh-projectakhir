# Generated by Django 5.1.1 on 2024-11-29 02:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MangaKabeh', '0010_order_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]