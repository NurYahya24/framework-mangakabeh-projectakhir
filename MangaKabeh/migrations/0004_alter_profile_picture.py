# Generated by Django 5.1.1 on 2024-11-26 20:12

import MangaKabeh.models.profile
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MangaKabeh', '0003_profile_delete_customer_alter_manga_seller_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='picture',
            field=models.ImageField(upload_to=MangaKabeh.models.profile.user_profile_upload_path),
        ),
    ]