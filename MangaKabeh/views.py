from collections import defaultdict
import json
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
import requests
from .decorators import group_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from .models import Manga, VolumeManga, Genre, Cart, CartItem, Order, OrderItem, Profile
from django.contrib.auth import login
from django.contrib.auth.models import Group, User
from .forms import MangaForm, VolumeFormSet, UserRegistrationForm
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from rest_framework import viewsets
from .serializers import MangaSerializer
# Create your views here.

def is_superuser(user):
    return user.is_superuser

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            
            # Create a Profile for the user if it doesn't exist
            if not hasattr(user, 'profile'):
                Profile.objects.create(user=user)  # Ensure profile is created

            # Set user role based on registration form data
            role = form.cleaned_data['role']
            group_name = role
            group = Group.objects.get(name=group_name)
            group.user_set.add(user)

            # Log in the user
            login(request, user)
            
            # Set profile active if role is 'Customer'
            if role == 'Customer':
                user.profile.is_active = True
                user.profile.save()  # Save the profile changes

            return redirect('home')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    if user.groups.filter(name='Seller').exists():
        return redirect('dashboard_seller')
    elif user.groups.filter(name='Customer').exists():
        return redirect('home')
    elif user.is_superuser:
        return redirect('dashboard_admin')
    return HttpResponseForbidden("You do not have permission to access this page.")
    
@user_passes_test(is_superuser)
def dashboard_admin(request):
    mangas = Manga.objects.all()
    return render(request, 'admin/admin_dashboard.html', {'mangas': mangas})

@group_required('Seller')
def dashboard_seller(request):
    mangas = Manga.objects.filter(seller = request.user)
    return render(request, 'seller/seller_dashboard.html', {'mangas': mangas})



from django.db.models import Min

def base(request):
    
    # Mengambil semua manga dengan harga volume termurah, urutkan berdasarkan ID terbalik (ID terbaru muncul di kiri)
    mangas = Manga.objects.all().annotate(min_price=Min('volumemanga__price')).order_by('-id')
    # mangas = Manga.objects.all().annotate(min_price=Min('volumemanga__price'))
    genre_aksi = Manga.objects.filter(genre__name__iexact="Aksi").annotate(min_price=Min('volumemanga__price'))
    genre_drama = Manga.objects.filter(genre__name__iexact="Drama").annotate(min_price=Min('volumemanga__price'))
    
    return render(request, 'base.html', {
        'mangas': mangas,
        'genre_aksi': genre_aksi,
        'genre_drama' : genre_drama,
    })

@group_required('Customer')
def add_to_cart(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            volume_id = data.get("volume_id")
            quantity = int(data.get("quantity", 1))

            # Get the volume and seller
            volume = get_object_or_404(VolumeManga, id=volume_id)
            seller = volume.manga.seller  # Assuming VolumeManga has a ForeignKey to Seller
            if volume.stock < int(quantity):
                return JsonResponse({"success": False, "message": "Not enough stock available."})

            # Get or create a cart for the user
            cart, created = Cart.objects.get_or_create(user=request.user)

            # Add or update the cart item
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, volume=volume, seller=seller,
                defaults={'quantity': quantity}
            )

            if not created:
                cart_item.quantity += quantity  # Increase quantity if item already exists
            else:
                cart_item.quantity = quantity  # Set the quantity if it's a new item

            cart_item.save()

            return JsonResponse({"success": True, "message": "Item added to cart"})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error: {str(e)}"})

    return JsonResponse({"success": False, "message": "Invalid request method"})


@group_required('Seller')
def manga_form_view(request, manga_id=None):
    manga = None
    if manga_id:
        manga = get_object_or_404(Manga, id=manga_id, seller=request.user)

    if request.method == "POST":
        print(request.POST)
        manga_form = MangaForm(request.POST, request.FILES, instance=manga)
        volume_formset = VolumeFormSet(request.POST, queryset=VolumeManga.objects.filter(manga=manga))

        if manga_form.is_valid() and volume_formset.is_valid():
            manga = manga_form.save(commit=False)
            manga.seller = request.user
            manga.save()

            # Save genres
            genre_data = manga_form.cleaned_data['genre']
            for genre_name in genre_data:
                genre, created = Genre.objects.get_or_create(name=genre_name)
                manga.genre.add(genre)

            # Save volumes
            volumes = volume_formset.save(commit=False)
            for volume in volumes:
                volume.manga = manga
                volume.save()

            for volume in volume_formset.deleted_objects:
                volume.delete()

            return redirect('dashboard_seller')
        else:
            print("Form Errors:", manga_form.errors)
            print("Formset Errors:", volume_formset.errors)
    else:
        manga_form = MangaForm(instance=manga)
        volume_formset = VolumeFormSet(
            queryset=VolumeManga.objects.filter(manga=manga) if manga else VolumeManga.objects.none()
        )
        for field in manga_form.fields.values():
            field.widget.attrs["class"] = "form-control"

    return render(request, 'seller/manga_form.html', {
        'form': manga_form,
        'volume_formset': volume_formset,
    })

@login_required
def profile(request):
    user = request.user
    
    # Retrieve the Profile for the logged-in user (if exists)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = None

    # Determine the profile type based on some condition, for example, user.role if available
    # You can also use any logic that works for your app's business rules.
    profile_type = None
    if profile:
        if hasattr(user, 'profile') and profile:
            if user.profile.is_active:
                if 'Seller' in user.groups.values_list('name', flat=True):
                    profile_type = 'Seller'
                elif 'Customer' in user.groups.values_list('name', flat=True):
                    profile_type = 'Customer'
    else:
        profile_type = 'Unknown'

    return render(request, 'profile.html', {
        'profile': profile,
        'profile_type': profile_type,
    })


def manga_detail(request, manga_id):
    query = manga_id
    
    mangaApi = []
    if query :
        response = requests.get(f'http://127.0.0.1:8000/api/manga/{query}')
        if response.status_code == 200:
            mangaApi = response.json()
        else :
            mangaApi = []
    manga = get_object_or_404(Manga, id=manga_id)
    volumes = VolumeManga.objects.filter(manga=manga)
    return render(request, 'customer/manga_detail.html', {'manga': mangaApi, 'volumes': volumes})

@group_required('Customer')
def view_cart(request):
    # Get the user's cart or return a 404 if not found
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    # Group items by seller
    items_by_seller = defaultdict(list)
    total_per_seller = defaultdict(list)
    total_cart_price = 0
    for item in cart_items:
        seller = item.seller
        item_total_price = item.quantity * item.volume.price  # Calculate total price per item
        
        # Add item to the corresponding seller's list
        items_by_seller[seller].append({
            'item': item,
            'total_price': item_total_price,
        })
        

    for seller, items in items_by_seller.items():
        total_per_seller[seller] = sum(item['total_price'] for item in items)
    
    total_per_seller = dict(total_per_seller)
    items_by_seller = dict(items_by_seller)
    # Pass the data to the template
    context = {
        'items_by_seller': items_by_seller,
        'total_per_seller': total_per_seller,
    }
    
    print("Items by Seller:", items_by_seller)

    return render(request, 'customer/cart.html', context)


@group_required('Customer')
def remove_cart_item(request):
    if request.method == "POST":
        cart_item_id = request.POST.get('cart_item_id')
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)

        cart_item.delete()

        # Add a success message
        messages.success(request, "Item removed from your cart.")
        return redirect('view_cart')

    # If the request method isn't POST, redirect back to the cart
    return redirect('view_cart')

@group_required('Customer')
def checkout(request, seller_id):
    # Get the cart for the current user
    cart = get_object_or_404(Cart, user=request.user)

    # Get items in the cart for the specified seller
    cart_items = cart.cart_items.select_related('volume').filter(volume__manga__seller_id=seller_id)

    if not cart_items:
        messages.error(request, "Your cart for this seller is empty.")
        return redirect('view_cart')

    # Calculate total price
    total_price = sum(item.quantity * item.volume.price for item in cart_items)

    # Create an Order object
    order = Order.objects.create(
        user=request.user,
        seller_id=seller_id,
        total_price=total_price,
        status='Pending'
    )

    # Create OrderItems for each CartItem and update stock
    for item in cart_items:
        # Check if there's enough stock
        if item.volume.stock >= item.quantity:
            # Decrease stock based on the ordered quantity
            item.volume.update_stock(item.quantity)

            # Create the corresponding OrderItem
            OrderItem.objects.create(
                order=order,
                volume=item.volume,
                quantity=item.quantity,
                price=item.volume.price
            )
        else:
            # If stock is insufficient, notify the user and stop the checkout process
            messages.error(request, f"Not enough stock for {item.volume.manga.title} volume.")
            return redirect('view_cart')

    # Clear the cart for this seller (delete items after order creation)
    cart_items.delete()

    # Success message
    seller_name = cart_items[0].volume.manga.seller.username if cart_items else "Seller"
    messages.success(request, f"Checkout successful for seller: {seller_name}. Total: Rp.{total_price}")

    # Redirect to the cart or another relevant page
    return redirect('view_cart')


@login_required
def order_list(request):
    filter_status = request.GET.get('status', 'Pending')

    # Check if the user is a seller
    is_seller = request.user.groups.filter(name='Seller').exists()

    if is_seller:
        # Filter orders where the seller matches the logged-in user
        orders = Order.objects.filter(seller=request.user, status=filter_status)
    else:
        # Filter orders where the user is the buyer
        orders = Order.objects.filter(user=request.user, status=filter_status)

    return render(request, 'order_list.html', {
        'orders': orders,
        'filter_status': filter_status,
        'is_seller': is_seller,
    })

@login_required
def cancel_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Check if the order is not already completed or canceled
        if order.status not in ['Done', 'Canceled']:
            # Update order status to 'Canceled'
            order.status = 'Canceled'
            
            # Restore the stock for each item in the canceled order
            for order_item in order.items.all():
                volume = order_item.volume
                volume.restock(order_item.quantity)  # Restoring stock
            
            order.save()
            messages.success(request, "Your order has been canceled, and stock has been restored.")

        return redirect('order_list')  # Replace with your order list view name

    return HttpResponseForbidden()

@login_required
def upload_payment(request, order_id):
    if request.method == 'POST' and 'payment' in request.FILES:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        if order.status == 'Pending':  # Only allow payment upload for pending orders
            order.payment = request.FILES['payment']
            order.save()
        return redirect('order_list')  # Replace with your order list view name
    return HttpResponseForbidden()

@login_required
def delete_photo(request, order_id):
    # Ensure only the buyer who uploaded the photo can delete it
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == "POST":
        if order.payment:
            order.payment.delete()  # Deletes the image file from storage
            order.payment = None   # Remove the reference in the database
            order.save()
            messages.success(request, f"Payment proof for Order {order_id} has been deleted.")
        else:
            messages.error(request, "No payment proof to delete.")
    return redirect("order_list")  # Redirect to your order list page

@login_required
def accept_order(request, order_id):
    # Ensure only sellers can accept orders
    order = get_object_or_404(Order, id=order_id, seller=request.user)

    if request.method == "POST":
        if order.status == "Pending":
            order.status = "On Process"
            order.save()
            messages.success(request, f"Order {order_id} has been accepted.")
        else:
            messages.error(request, "Order status is not valid for acceptance.")
    return redirect("order_list")  # Redirect to your order list page

@login_required
def done_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, user=request.user)
        if order.status not in ['Done', 'Canceled']:
            order.status = 'Done'
            order.save()
        return redirect('order_list')  # Replace with your order list view name
    return HttpResponseForbidden()

@user_passes_test(is_superuser)
def manage_accounts(request):
    users = User.objects.all()  # List all users

    # Handle activating or deactivating user accounts
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')

        try:
            user = User.objects.get(id=user_id)
            profile = user.profile
            if action == 'activate':
                profile.is_active = True
            else:
                profile.is_active = False
            profile.save()

            # Optionally redirect to a success message or stay on the same page
            return redirect('manage_accounts')

        except User.DoesNotExist:
            pass  # Handle user not found if needed

    return render(request, 'admin/manage_users.html', {'users': users})

@user_passes_test(is_superuser)
def delete_manga(request, manga_id):
    try:
        manga = Manga.objects.get(id=manga_id)
        manga.delete()
        messages.success(request, 'Manga deleted successfully!')
    except Manga.DoesNotExist:
        messages.error(request, 'Manga not found!')
    return redirect('dashboard')

@group_required('Seller')
def delete_manga_seller(request, manga_id):
    try:
        manga = Manga.objects.get(id=manga_id)
        seller = manga.seller
        if seller == request.user:
            manga.delete()
            messages.success(request, 'Manga deleted successfully!')
        else :
            messages.error(request, 'No Permission')
    except Manga.DoesNotExist:
        messages.error(request, 'Manga not found!')
    return redirect('dashboard')

def search_manga(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        results = Manga.objects.annotate(
            min_price=Min('volumemanga__price')  # Anotasi harga minimum
        ).filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(genre__name__icontains=query)
        ).distinct()
    return render(request, 'search_results.html', {'query': query, 'results': results})

@user_passes_test(is_superuser)
def add_genre(request):
    if request.method == "POST":
        name = request.POST.get('name')
        if name:
            Genre.objects.create(name=name)
            messages.success(request, "Genre added successfully.")
        else:
            messages.error(request, "Genre name cannot be empty.")
    return redirect('dashboard')

#api
class MangaViewSet(viewsets.ModelViewSet):
    queryset = Manga.objects.all()
    serializer_class = MangaSerializer