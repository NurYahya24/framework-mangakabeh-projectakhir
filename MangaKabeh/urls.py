from django.urls import include, path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('', views.base, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('manga/<int:manga_id>/', views.manga_detail, name='manga_detail'),
    path('manga/admin/delete/<int:manga_id>/', views.delete_manga, name='delete_manga'),
    path('manga/seller/delete/<int:manga_id>/', views.delete_manga_seller, name='delete_manga_seller'),
    path('orders/', views.order_list, name='order_list'),
    path('accept_order/<int:order_id>/', views.accept_order, name='accept_order'),
    path('delete_photo/<int:order_id>/', views.delete_photo, name='delete_photo'),
    #===================ATMIN===========================
    path('admins/dashboard/', views.dashboard_admin, name='dashboard_admin'),
    path('admins/manage_accounts/', views.manage_accounts, name='manage_accounts'),
    #===================CUSTOMER========================
    path('customer/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('customer/cart', views.view_cart, name='view_cart'),
    path('customer/cart/remove/', views.remove_cart_item, name='remove_cart_item'),
    path('customer/checkout/<int:seller_id>/', views.checkout, name='checkout'),
    path('customer/order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('customer/order/<int:order_id>/done/', views.done_order, name='done_order'),
    path('customer/order/<int:order_id>/upload-payment/', views.upload_payment, name='upload_payment'),
    #===================SELLER==========================
    path('seller/dashboard/', views.dashboard_seller, name='dashboard_seller'),
    path('seller/add-manga/', views.manga_form_view, name='add_manga'),
    path('seller/update-manga/<int:manga_id>/', views.manga_form_view, name='edit_manga'),
    #===================ACCOUNT=================================
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
]

