# Generated by Django 5.1.1 on 2024-11-24 00:42

import MangaKabeh.models.manga
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MangaKabeh', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manga',
            name='image',
            field=models.ImageField(upload_to=MangaKabeh.models.manga.manga_image_upload_path),
        ),
    ]
