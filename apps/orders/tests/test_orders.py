from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.products.models import Product, Category
from apps.orders.models import Order, OrderItem
from decimal import Decimal


class CartViewTests(TestCase):
    """Tests for shopping cart functionality"""

    def setUp(self):
        self.client = Client()
        self.cart_url = reverse('cart_view')

        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Test Product',
            price=Decimal('99.99'),
            category=self.category,
            stock=10
        )

        self.customer = User.objects.create_user(
            username='customer',
            password='pass123',
            user_type='customer',
            address='Test Address'
        )

        self.courier = User.objects.create_user(
            username='courier',
            password='pass123',
            user_type='courier'
        )

    def test_cart_requires_login(self):
        """Test cart requires authentication"""
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, 302)

    def test_cart_loads_for_customer(self):
        """Test cart page loads for customers"""
        self.client.force_login(self.customer)
        response = self.client.get(self.cart_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/cart.html')

    def test_cart_redirects_courier(self):
        """Test couriers are redirected from cart"""
        self.client.force_login(self.courier)
        response = self.client.get(self.cart_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('courier_orders'))

    def test_add_to_cart_success(self):
        """Test adding product to cart"""
        self.client.force_login(self.customer)
        add_url = reverse('add_to_cart', kwargs={'product_id': self.product.id})

        response = self.client.post(add_url)
        self.assertEqual(response.status_code, 302)

        session = self.client.session
        self.assertIn(str(self.product.id), session.get('cart', {}))

    def test_add_to_cart_courier_denied(self):
        """Test couriers cannot add to cart"""
        self.client.force_login(self.courier)
        add_url = reverse('add_to_cart', kwargs={'product_id': self.product.id})

        response = self.client.post(add_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('courier_orders'))

    def test_add_to_cart_increases_quantity(self):
        """Test adding same product increases quantity"""
        self.client.force_login(self.customer)
        add_url = reverse('add_to_cart', kwargs={'product_id': self.product.id})

        self.client.post(add_url)
        self.client.post(add_url)

        session = self.client.session
        cart = session.get('cart', {})
        self.assertEqual(cart[str(self.product.id)]['quantity'], 2)

    def test_remove_from_cart(self):
        """Test removing product from cart"""
        self.client.force_login(self.customer)

        session = self.client.session
        session['cart'] = {str(self.product.id): {'quantity': 1, 'price': '99.99', 'name': 'Test'}}
        session.save()

        remove_url = reverse('remove_from_cart', kwargs={'product_id': self.product.id})
        response = self.client.post(remove_url)

        self.assertEqual(response.status_code, 302)
        session = self.client.session
        self.assertNotIn(str(self.product.id), session.get('cart', {}))

    def test_cart_total_calculation(self):
        """Test cart total is calculated correctly"""
        self.client.force_login(self.customer)

        session = self.client.session
        session['cart'] = {
            str(self.product.id): {
                'quantity': 2,
                'price': '99.99',
                'name': 'Test Product',
                'image': None
            }
        }
        session.save()

        response = self.client.get(self.cart_url)
        self.assertEqual(response.context['total'], 199.98)


class OrderCreateTests(TestCase):
    """Tests for order creation functionality"""

    def setUp(self):
        self.client = Client()
        self.create_url = reverse('create_order')

        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Test Product',
            price=Decimal('99.99'),
            category=self.category,
            stock=10
        )

        self.customer = User.objects.create_user(
            username='customer',
            password='pass123',
            user_type='customer'
        )

    def test_create_order_requires_login(self):
        """Test order creation requires authentication"""
        response = self.client.post(self.create_url)
        self.assertEqual(response.status_code, 302)

    def test_create_order_success(self):
        """Test successful order creation"""
        self.client.force_login(self.customer)

        session = self.client.session
        session['cart'] = {
            str(self.product.id): {
                'quantity': 1,
                'price': '99.99',
                'name': 'Test Product'
            }
        }
        session.save()

        data = {
            'full_name': 'Test Customer',
            'delivery_address': 'Test Address 123',
            'delivery_date': '2025-12-31',
            'notes': 'Test notes'
        }

        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, 302)

        self.assertTrue(Order.objects.filter(customer=self.customer).exists())
        order = Order.objects.get(customer=self.customer)
        self.assertEqual(order.full_name, 'Test Customer')
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total_price, Decimal('99.99'))

    def test_create_order_empty_cart(self):
        """Test order creation fails with empty cart"""
        self.client.force_login(self.customer)

        data = {
            'full_name': 'Test Customer',
            'delivery_address': 'Test Address 123'
        }

        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Order.objects.filter(customer=self.customer).exists())

    def test_create_order_saves_delivery_data(self):
        """Test saving delivery data to user profile"""
        self.client.force_login(self.customer)

        session = self.client.session
        session['cart'] = {
            str(self.product.id): {
                'quantity': 1,
                'price': '99.99',
                'name': 'Test Product'
            }
        }
        session.save()

        data = {
            'full_name': 'Test Customer',
            'delivery_address': 'New Address 456',
            'save_delivery_data': True
        }

        response = self.client.post(self.create_url, data)

        self.customer.refresh_from_db()
        self.assertEqual(self.customer.address, 'New Address 456')


class OrderListViewTests(TestCase):
    """Tests for order list view functionality"""

    def setUp(self):
        self.client = Client()
        self.list_url = reverse('order_list')

        self.customer = User.objects.create_user(
            username='customer',
            password='pass123',
            user_type='customer'
        )

        self.courier = User.objects.create_user(
            username='courier',
            password='pass123',
            user_type='courier'
        )

        self.order1 = Order.objects.create(
            customer=self.customer,
            status='pending',
            full_name='Test',
            delivery_address='Address',
            total_price=Decimal('100.00')
        )

        self.order2 = Order.objects.create(
            customer=self.customer,
            status='delivered',
            full_name='Test',
            delivery_address='Address',
            total_price=Decimal('200.00')
        )

    def test_order_list_requires_login(self):
        """Test order list requires authentication"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 302)

    def test_order_list_loads_for_customer(self):
        """Test order list loads for customers"""
        self.client.force_login(self.customer)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_list.html')

    def test_order_list_redirects_courier(self):
        """Test couriers are redirected from order list"""
        self.client.force_login(self.courier)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('courier_orders'))

    def test_order_list_shows_active_orders(self):
        """Test active orders are displayed separately"""
        self.client.force_login(self.customer)
        response = self.client.get(self.list_url)

        active_orders = response.context['active_orders']
        self.assertEqual(len(active_orders), 1)
        self.assertEqual(active_orders[0].status, 'pending')

    def test_order_list_shows_finished_orders(self):
        """Test finished orders are displayed separately"""
        self.client.force_login(self.customer)
        response = self.client.get(self.list_url)

        finished_orders = response.context['finished_orders']
        self.assertEqual(len(finished_orders), 1)
        self.assertEqual(finished_orders[0].status, 'delivered')


class CancelOrderTests(TestCase):
    """Tests for order cancellation functionality"""

    def setUp(self):
        self.client = Client()

        self.customer = User.objects.create_user(
            username='customer',
            password='pass123',
            user_type='customer'
        )

        self.courier = User.objects.create_user(
            username='courier',
            password='pass123',
            user_type='courier'
        )

        self.order = Order.objects.create(
            customer=self.customer,
            status='pending',
            full_name='Test',
            delivery_address='Address',
            total_price=Decimal('100.00')
        )

        self.cancel_url = reverse('cancel_order', kwargs={'order_id': self.order.id})

    def test_cancel_order_requires_login(self):
        """Test order cancellation requires authentication"""
        response = self.client.post(self.cancel_url)
        self.assertEqual(response.status_code, 302)

    def test_cancel_order_success(self):
        """Test successful order cancellation"""
        self.client.force_login(self.customer)
        response = self.client.post(self.cancel_url)

        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'cancelled')

    def test_cancel_delivered_order_fails(self):
        """Test cannot cancel delivered orders"""
        self.order.status = 'delivered'
        self.order.save()

        self.client.force_login(self.customer)
        response = self.client.post(self.cancel_url)

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'delivered')

    def test_cancel_order_courier_denied(self):
        """Test couriers cannot cancel orders"""
        self.client.force_login(self.courier)
        response = self.client.post(self.cancel_url)

        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'pending')

    def test_cancel_other_user_order_fails(self):
        """Test users cannot cancel other users' orders"""
        other_customer = User.objects.create_user(
            username='other',
            password='pass123',
            user_type='customer'
        )

        self.client.force_login(other_customer)
        response = self.client.post(self.cancel_url)

        self.assertEqual(response.status_code, 404)
