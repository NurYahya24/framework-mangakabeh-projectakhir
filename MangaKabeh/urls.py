from django.urls import include, path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('', views.base, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('manga/<int:manga_id>/', views.manga_detail, name='manga_detail'),
    path('orders/', views.order_list, name='order_list'),
    #===================ATMIN===========================
    path('admins/dashboard/', views.dashboard_admin, name='dashboard_admin'),
    #===================CUSTOMER========================
    path('customer/dashboard/', views.dashboard_customer, name='dashboard_customer'),
    path('customer/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('customer/cart', views.view_cart, name='view_cart'),
    path('customer/cart/remove/', views.remove_cart_item, name='remove_cart_item'),
    path('customer/checkout/<int:seller_id>/', views.checkout, name='checkout'),
    #===================SELLER==========================
    path('seller/dashboard/', views.dashboard_seller, name='dashboard_seller'),
    path('seller/add-manga/', views.manga_form_view, name='add_manga'),
    path('seller/update-manga/<int:manga_id>/', views.manga_form_view, name='edit_manga'),
    #===================ACCOUNT=================================
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
]

