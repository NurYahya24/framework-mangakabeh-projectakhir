from django.urls import include, path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('', views.base, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    #===================ATMIN===========================
    path('admins/dashboard/', views.dashboard_admin, name='dashboard_admin'),
    #===================CUSTOMER========================
    path('customer/dashboard/', views.dashboard_customer, name='dashboard_customer'),
    
    #===================SELLER==========================
    path('seller/dashboard/', views.dashboard_seller, name='dashboard_seller'),
    path('seller/add-manga/', views.add_manga, name='add_manga'),
    path('seller/manage-orders', views.manage_orders, name='manage_orders'),
    #====================================================
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
     path('register/', views.register, name='register'),
]

