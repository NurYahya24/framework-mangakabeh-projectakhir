# Generated by Django 5.1.1 on 2024-11-23 20:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('phone_number', models.CharField(max_length=13, unique=True)),
                ('username', models.CharField(max_length=255, unique=True)),
                ('address', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Seller',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('phone_number', models.CharField(max_length=13, unique=True)),
                ('username', models.CharField(max_length=255, unique=True)),
                ('address', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Manga',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('author', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('image', models.ImageField(upload_to='manga/<django.db.models.fields.related.ForeignKey>/<django.db.models.fields.CharField>/')),
                ('genre', models.ManyToManyField(to='MangaKabeh.genre')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='MangaKabeh.seller')),
            ],
        ),
        migrations.CreateModel(
            name='VolumeManga',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('volume', models.CharField(default='1', max_length=128)),
                ('price', models.IntegerField()),
                ('manga', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='MangaKabeh.manga')),
            ],
        ),
    ]
