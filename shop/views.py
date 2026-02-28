from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Product, Category, Manufacturer, Cart, CartItem

def home_view(request):
    return render(request, 'shop/home.html')

def author_view(request):
    return HttpResponse("Сайт разработал: Скорик Илья, группа 87ТП")

def about_view(request):
    return HttpResponse('Добро пожаловать в хобби-гипермаркет "Леонард"')


def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    manufacturers = Manufacturer.objects.all()

    category_id = request.GET.get('category')
    manufacturer_id = request.GET.get('manufacturer')
    search_query = request.GET.get('search')

    if category_id:
        products = products.filter(category_id=category_id)

    if manufacturer_id:
        products = products.filter(manufacturer_id=manufacturer_id)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    context = {
        'products': products,
        'categories': categories,
        'manufacturers': manufacturers
    }

    return render(request, 'shop/product_list.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}   # ← ВОТ ЭТО ГЛАВНОЕ
    )

    if not created:
        if cart_item.quantity + 1 <= product.stock_quantity:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.error(request, "Недостаточно товара на складе.")

    return redirect('cart')

@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))

        if quantity <= cart_item.product.stock_quantity:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            messages.error(request, "Количество превышает остаток на складе.")

    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart')

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    total_price = cart.total_price()

    return render(request, 'shop/cart.html', {
        'cart': cart,
        'items': items,
        'total_price': total_price
    })