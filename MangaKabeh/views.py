from collections import defaultdict
import json
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from .decorators import group_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from .models import Manga, VolumeManga, Genre, Cart, CartItem, Order, OrderItem
from django.contrib.auth import login
from django.contrib.auth.models import Group
from .forms import MangaForm, VolumeFormSet, UserRegistrationForm
# Create your views here.

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            role = form.cleaned_data['role']
            group_name = role
            group = Group.objects.get(name=group_name)
            group.user_set.add(user)
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form':form})

@login_required
def dashboard(request):
    user = request.user
    if user.groups.filter(name='Admin').exists():
        return redirect('dashboard_admin')
    elif user.groups.filter(name='Seller').exists():
        return redirect('dashboard_seller')
    elif user.groups.filter(name='Customer').exists():
        return redirect('dashboard_customer')
    elif user.is_superuser:
        return redirect('/admin/')
    return HttpResponseForbidden("You do not have permission to access this page.")
    
@group_required('Admin')
def dashboard_admin(request):
    return render(request, 'admin/admin_dashboard.html', {})

@group_required('Seller')
def dashboard_seller(request):
    mangas = Manga.objects.filter(seller = request.user)
    return render(request, 'seller/seller_dashboard.html', {'mangas': mangas})

@group_required('Customer')
def dashboard_customer(request):
    return render(request, 'customer/customer_dashboard.html')



from django.db.models import Min

def base(request):
    
    # Mengambil semua manga dengan harga volume termurah
    mangas = Manga.objects.all().annotate(min_price=Min('volumemanga__price'))
    
    return render(request, 'base.html', {
        'mangas': mangas,
    })

@group_required('Customer')
def add_to_cart(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print(data)
            volume_id = data.get("volume_id")
            quantity = int(data.get("quantity", 1))

            # Get the volume and seller
            volume = get_object_or_404(VolumeManga, id=volume_id)
            seller = volume.manga.seller  # Assuming VolumeManga has a ForeignKey to Seller

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

    profile = None


    return render(request, 'profile.html', {
        'profile': profile,
    })


def manga_detail(request, manga_id):
    manga = get_object_or_404(Manga, id=manga_id)
    volumes = VolumeManga.objects.filter(manga=manga)
    return render(request, 'customer/manga_detail.html', {'manga': manga, 'volumes': volumes})

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
        status = 'Pending'
    )

    # Create OrderItems for each CartItem
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            volume=item.volume,
            quantity=item.quantity,
            price = item.volume.price
        )

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
    is_seller = request.user.groups.filter(name='seller').exists()

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