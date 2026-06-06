from django.contrib import admin
from .models import Manufacturer, Category, Product, Cart, CartItem, Order, OrderItem, Profile

admin.site.register(Manufacturer)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'phone', 'delivery_city', 'role_display']
    list_select_related = ['user', 'favorite_category']

    def role_display(self, obj):
        return obj.role_display()
    role_display.short_description = 'Роль'
