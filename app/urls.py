from django.urls import path
from .import views

urlpatterns=[
    path('',views.home,name="home"),
    path('register/',views.registration,name='register'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('brand_search/',views.brand_search,name='brand_search'),
    path('view_product/<str:brand>',views.view_product,name='view_product'),
    path('view_product/', views.view_product, name='view_product_all'),
    path('uniq_detaild/<int:id>',views.uniq_detaild,name='uniq_detaild'),
    path('handil_action/<int:id>',views.handil_action,name='handil_action'),
    path('view_cart/',views.view_cart,name='view_cart'),
    path('add_cart/<int:id>',views.add_cart,name='add_cart'),
    path('remove/<int:id>',views.remove,name='remove'),
    path('buy_from_cart/<int:id>',views.buy_from_cart,name='buy_from_cart'),
    path('buy_from_cart_all/',views.buy_from_cart,name='buy_from_cart_all'),
    path('payment_susses/',views.payment_susses,name='payment_susses'),
    # -----------------------------------------
    
    path('cart_checkout_id/<int:id>',views.cart_checkout,name='cart_checkout_id'),
    path('cart_checkout',views.cart_checkout,name='cart_checkout'),
    path('payment_root',views.payment_root,name='payment_root'),
    path('payment_root_id/<int:id>',views.payment_root,name='payment_root_id'),
    path('Profile/',views.profile,name='Profile'),
    path('profileUpdate/<int:id>',views.profileupdate,name='profileUpdate'),
    path('myorder/',views.myordars,name='myorder'),
    
    
    # direct
    # path('direct_checkout/<int:id>',views.payment_root,name='payment_root_id'),
    
    
]