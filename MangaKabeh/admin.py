from django.contrib import admin

from MangaKabeh.models.cart import Cart, CartItem
from .models.manga import Manga, VolumeManga, Genre
from .models.profile import Profile
from .models.order import Order, OrderItem
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
    

class UserAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0  # Prevent extra blank fields by default
    readonly_fields = ('volume', 'quantity')  # Make fields read-only if necessary
    can_delete = False  # Prevent deletion through admin if required

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')  # Customize the columns in the cart list
    inlines = [CartItemInline]
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'volume', 'quantity')
    list_filter = ('cart__user',)  # Add filters for better navigation
    search_fields = ('cart__user__username', 'volume__manga__title')  # Add search fields

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # Set to 0 to not show empty forms for additional items
    readonly_fields = ('volume', 'quantity')  # Make fields read-only

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'seller', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')  # Add filters for status and date
    search_fields = ('user__username', 'seller__username')  # Add search bar for users/sellers
    inlines = [OrderItemInline]  # Show related items in the same form
    readonly_fields = ('user', 'seller', 'total_price', 'created_at')  # Make fields read-only where needed

    # Optional: Customize the detail view layout
    fieldsets = (
        ('Order Details', {
            'fields': ('user', 'seller', 'total_price', 'status', 'created_at')
        }),
    )

admin.site.register(Order, OrderAdmin) 
admin.site.register(Profile, UserAdmin)
admin.site.register(Manga, MangaAdmin)
admin.site.register(Genre)