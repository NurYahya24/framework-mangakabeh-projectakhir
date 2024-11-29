from rest_framework import serializers
from .models import Manga, Genre

      
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'
        
class MangaSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    class Meta:
        model = Manga
        fields = '__all__'