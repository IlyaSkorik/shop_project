from django.urls import path
from . import views

urlpatterns = [
    path('author/', views.author_view, name='author'),
    path('about/', views.about_view, name='about'),
    path('', views.home_view, name='home'),
    
    # Каталог
    path('catalog/', views.product_list, name='product_list'),
    path('catalog/<int:pk>/', views.product_detail, name='product_detail'),

    # Корзина
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
]