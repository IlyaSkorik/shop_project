from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse

from .models import Category, Manufacturer, Product, Order, OrderItem, Profile


def make_groups():
    Group.objects.get_or_create(name='Покупатель')
    Group.objects.get_or_create(name='Администратор')


def make_product(category, manufacturer):
    return Product.objects.create(
        name='Тестовый товар',
        description='Описание',
        price='99.99',
        stock_quantity=10,
        category=category,
        manufacturer=manufacturer,
    )


class GuestCatalogTest(TestCase):
    """Сценарий 1: Гость открывает каталог — успех."""

    def setUp(self):
        make_groups()
        cat = Category.objects.create(name='Краски')
        mfr = Manufacturer.objects.create(name='Завод', country='BY')
        make_product(cat, mfr)

    def test_guest_can_view_catalog(self):
        resp = self.client.get(reverse('product_list'))
        self.assertEqual(resp.status_code, 200)

    def test_guest_can_view_api_products(self):
        resp = self.client.get('/api/products/')
        self.assertEqual(resp.status_code, 200)


class GuestProfileChangeTest(TestCase):
    """Сценарий 2: Гость пытается изменить профиль — 401."""

    def test_guest_patch_me_returns_403_or_401(self):
        resp = self.client.patch(
            '/api/me/',
            data='{"full_name": "Хакер"}',
            content_type='application/json',
        )
        self.assertIn(resp.status_code, [401, 403])

    def test_guest_cabinet_redirects_to_login(self):
        resp = self.client.get(reverse('cabinet'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login', resp['Location'])


class CustomerCabinetTest(TestCase):
    """Сценарий 3: Покупатель открывает личный кабинет — успех."""

    def setUp(self):
        make_groups()
        self.user = User.objects.create_user(username='buyer', password='pass1234')
        group = Group.objects.get(name='Покупатель')
        self.user.groups.add(group)
        Profile.objects.get_or_create(user=self.user)
        self.client.login(username='buyer', password='pass1234')

    def test_customer_can_open_cabinet(self):
        resp = self.client.get(reverse('cabinet'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Личный кабинет')

    def test_customer_can_get_api_me(self):
        resp = self.client.get('/api/me/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['username'], 'buyer')
        self.assertEqual(data['role'], 'Покупатель')


class CustomerCreateProductTest(TestCase):
    """Сценарий 4: Покупатель пытается создать товар — 403."""

    def setUp(self):
        make_groups()
        cat = Category.objects.create(name='Холсты')
        mfr = Manufacturer.objects.create(name='Завод', country='BY')
        self.cat_id = cat.id
        self.mfr_id = mfr.id
        self.user = User.objects.create_user(username='buyer2', password='pass1234')
        self.user.groups.add(Group.objects.get(name='Покупатель'))
        self.client.login(username='buyer2', password='pass1234')

    def test_customer_cannot_create_product(self):
        resp = self.client.post(
            '/api/products/',
            data={
                'name': 'Новый товар',
                'description': 'test',
                'price': '10.00',
                'stock_quantity': 5,
                'category': self.cat_id,
                'manufacturer': self.mfr_id,
            },
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 403)


class AdminProductTest(TestCase):
    """Сценарий 5: Администратор создаёт и редактирует товар — успех."""

    def setUp(self):
        make_groups()
        cat = Category.objects.create(name='Кисти')
        mfr = Manufacturer.objects.create(name='Арт-завод', country='BY')
        self.cat_id = cat.id
        self.mfr_id = mfr.id
        self.admin = User.objects.create_user(username='admin1', password='admin1234', is_staff=True)
        self.admin.groups.add(Group.objects.get(name='Администратор'))
        self.client.login(username='admin1', password='admin1234')

    def test_admin_can_create_product(self):
        resp = self.client.post(
            '/api/products/',
            data={
                'name': 'Кисть №8',
                'description': 'Мягкая',
                'price': '5.50',
                'stock_quantity': 20,
                'category': self.cat_id,
                'manufacturer': self.mfr_id,
            },
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 201)

    def test_admin_can_patch_product(self):
        cat = Category.objects.get(id=self.cat_id)
        mfr = Manufacturer.objects.get(id=self.mfr_id)
        product = make_product(cat, mfr)
        resp = self.client.patch(
            f'/api/products/{product.id}/',
            data={'price': '12.00'},
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['price'], '12.00')


class CustomerOrdersTest(TestCase):
    """Сценарий 6: Покупатель видит только свои заказы."""

    def setUp(self):
        make_groups()
        cat = Category.objects.create(name='Бумага')
        mfr = Manufacturer.objects.create(name='Завод', country='BY')
        product = make_product(cat, mfr)

        self.buyer = User.objects.create_user(username='buyer3', password='pass1234')
        self.buyer.groups.add(Group.objects.get(name='Покупатель'))

        other = User.objects.create_user(username='other', password='pass1234')
        other.groups.add(Group.objects.get(name='Покупатель'))

        self.my_order = Order.objects.create(
            user=self.buyer,
            email='buyer3@test.com',
            shipping_address='Минск',
            total_price='50.00',
        )
        OrderItem.objects.create(
            order=self.my_order,
            product=product,
            product_name=product.name,
            price=product.price,
            quantity=1,
        )

        other_order = Order.objects.create(
            user=other,
            email='other@test.com',
            shipping_address='Гродно',
            total_price='30.00',
        )
        OrderItem.objects.create(
            order=other_order,
            product=product,
            product_name=product.name,
            price=product.price,
            quantity=1,
        )

        self.client.login(username='buyer3', password='pass1234')

    def test_buyer_sees_only_own_orders(self):
        resp = self.client.get('/api/orders/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        orders = data if isinstance(data, list) else data.get('results', data)
        ids = [o['id'] for o in orders]
        self.assertIn(self.my_order.id, ids)
        self.assertEqual(len(ids), 1)

    def test_cabinet_shows_own_orders(self):
        resp = self.client.get(reverse('cabinet'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, str(self.my_order.id))
