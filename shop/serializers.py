from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Cart, CartItem, Category, Manufacturer, Order, OrderItem, Product


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]
        read_only_fields = fields


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ["id", "name", "country", "description"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    manufacturer_name = serializers.CharField(source="manufacturer.name", read_only=True)
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, product):
        if not product.product_image:
            return ""

        try:
            url = product.product_image.url
        except ValueError:
            return ""

        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "product_image",
            "price",
            "stock_quantity",
            "category",
            "category_name",
            "manufacturer",
            "manufacturer_name",
            "image_url",
        ]
        extra_kwargs = {
            "description": {"required": False, "allow_blank": True},
            "product_image": {"required": False, "allow_null": True},
            "stock_quantity": {"required": False, "default": 0},
        }


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = CartItem
        fields = ["id", "cart", "product", "product_name", "quantity", "total_price"]


class CartSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Cart
        fields = ["id", "user", "created_at", "items", "total_price"]
        read_only_fields = ["created_at"]


class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "order",
            "product",
            "product_name",
            "price",
            "quantity",
            "total_price",
        ]
        extra_kwargs = {
            "product_name": {"required": False},
            "price": {"required": False},
        }


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "email",
            "shipping_address",
            "total_price",
            "created_at",
            "items",
        ]
        read_only_fields = ["created_at", "total_price"]
