from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='api-products')
router.register(r'categories', views.CategoryViewSet, basename='api-categories')
router.register(r'manufacturers', views.ManufacturerViewSet, basename='api-manufacturers')
router.register(r'carts', views.CartViewSet, basename='api-carts')
router.register(r'cart-items', views.CartItemViewSet, basename='api-cart-items')
router.register(r'orders', views.OrderViewSet, basename='api-orders')
router.register(r'order-items', views.OrderItemViewSet, basename='api-order-items')

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
    path('checkout/', views.checkout, name='checkout'),
    path('api/', include(router.urls)),
]
