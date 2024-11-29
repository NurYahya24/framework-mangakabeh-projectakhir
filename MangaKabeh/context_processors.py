def navbar(request):
    user = request.user
    navbar_user_group = None
    if user.is_authenticated:
        if user.is_superuser:
            navbar_user_group = 'Admin'
        elif user.groups.filter(name = 'Customer').exists():
            navbar_user_group = 'Customer'
        elif user.groups.filter(name = 'Seller').exists():
            navbar_user_group = 'Seller'
    return{
        'navbar_user_group' : navbar_user_group,
        'authenticated' : user.is_authenticated,
    }