from django.shortcuts import render, redirect
from .decorators import group_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from .models.customer import Customer
from .models.seller import Seller
from .models import Manga
from .forms import MangaForm
# Create your views here.

def register(request):
    # Your registration logic here
    return render(request, 'register.html')

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
    user_group = 'Admin'
    return render(request, 'admin/admin_dashboard.html', {'user_group' : user_group})

@group_required('Seller')
def dashboard_seller(request):
    user_group = 'Seller'
    seller = Seller.objects.get(email=request.user.email)
    mangas = Manga.objects.filter(seller=seller)
    return render(request, 'seller/seller_dashboard.html', {'user_group' : user_group, 'mangas': mangas})

@group_required('Customer')
def dashboard_customer(request):
    user_group = 'Customer'
    return render(request, 'customer/customer_dashboard.html', {'user_group' : user_group})


def base(request):
    user_group = None
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Customer').exists():
            user_group = 'Customer'
        elif request.user.groups.filter(name='Seller').exists():
            user_group = 'Seller'
        elif request.user.groups.filter(name='Admin').exists():
            user_group = 'Admin'
    mangas = Manga.objects.all()
    return render(request, 'base.html', {'user_group': user_group, 'mangas': mangas})

@group_required('Seller')
def add_manga(request):
    user_group = 'Seller'
    if request.method == "POST":
        manga_form = MangaForm(request.POST)
        if manga_form.is_valid():
            manga = manga_form.save(commit=False)
            manga.seller = request.user
            manga.save()
            
            return redirect('dashboard_seller')  
    else:
        manga_form = MangaForm()
    
    return render(request, 'seller/manga_form.html', {
        'manga_form': manga_form,
        'user_group': user_group
    })
def manage_orders(request):
    user_group = 'Seller'
    return render(request, 'seller/order_management.html', {'user_group': user_group})


@login_required
def profile(request):
    user = request.user
    is_seller = Seller.objects.filter(email=user.email).exists()
    is_customer = Customer.objects.filter(email=user.email).exists()

    profile = None
    profile_type = None

    if is_seller:
        profile_type = 'Seller'
        profile = Seller.objects.get(email=user.email)
    elif is_customer:
        profile_type = 'Customer'
        profile = Customer.objects.get(email=user.email)

    return render(request, 'profile.html', {
        'user': user,
        'profile_type': profile_type,
        'profile': profile,
    })
