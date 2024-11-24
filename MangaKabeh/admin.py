from django.contrib import admin
from .models.customer import Customer
from .models.seller import Seller
from .models.manga import Manga, VolumeManga, Genre
# Register your models here.

class VolumeMangaInline(admin.TabularInline):
    model = VolumeManga
    extra = 1
    
class MangaAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'get_genres')
    inlines = [VolumeMangaInline]
    filter_horizontal = ('genre',)
    
    def get_genres(self, obj):
        return ",".join([genre.name for genre in obj.genre.all()])
    get_genres.short_description = 'Genres'
    

    

admin.site.register(Customer)
admin.site.register(Seller)
admin.site.register(Manga, MangaAdmin)
admin.site.register(Genre)