from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.products.models import Product, Category
from apps.orders.models import Order
from decimal import Decimal


class CustomerE2EFlowTest(TestCase):
    """
    Tests the full E2E flow for a customer:
    Login -> Add to Cart -> Checkout.
    """

    def setUp(self):
        self.client = Client()

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

        self.add_to_cart_url = reverse('add_to_cart', kwargs={'product_id': self.product.id})
        self.create_order_url = reverse('create_order')

    def test_customer_full_order_flow(self):
        """
        Tests the complete cycle from adding a product to creating an order.
        """
        self.client.force_login(self.customer)

        response = self.client.post(self.add_to_cart_url)
        self.assertEqual(response.status_code, 302)

        session = self.client.session
        cart = session.get('cart', {})
        self.assertIn(str(self.product.id), cart)
        self.assertEqual(cart[str(self.product.id)]['quantity'], 1)

        order_data = {
            'full_name': 'Test Customer',
            'delivery_address': 'New Address 123',
            'delivery_date': '2025-12-31',
            'notes': 'Test notes'
        }

        self.assertEqual(Order.objects.count(), 0)

        response = self.client.post(self.create_order_url, order_data)

        self.assertEqual(response.status_code, 302)

        self.assertTrue(Order.objects.filter(customer=self.customer).exists())
        order = Order.objects.get(customer=self.customer)

        self.assertEqual(order.full_name, 'Test Customer')
        self.assertEqual(order.total_price, Decimal('99.99'))
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().product, self.product)

        session = self.client.session
        self.assertEqual(session.get('cart'), {})


class CourierE2EFlowTest(TestCase):
    """
    Tests the full E2E flow for a courier:
    Login -> Accept Order -> Update Statuses -> Deliver.
    """

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

        self.available_order = Order.objects.create(
            customer=self.customer,
            status='pending',
            full_name='Test',
            delivery_address='Address',
            total_price=Decimal('100.00')
        )

        self.accept_url = reverse('accept_order', kwargs={'order_id': self.available_order.id})
        self.update_url = reverse('update_order_status', kwargs={'order_id': self.available_order.id})
        self.orders_list_url = reverse('courier_orders')

    def test_courier_full_delivery_flow(self):
        """
        Tests the complete cycle from accepting an order to its delivery.
        """
        self.client.force_login(self.courier)

        response = self.client.get(self.orders_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.available_order, response.context['available_orders'])

        response = self.client.post(self.accept_url)
        self.assertEqual(response.status_code, 302)

        self.available_order.refresh_from_db()
        self.assertEqual(self.available_order.courier, self.courier)
        self.assertEqual(self.available_order.status, 'confirmed')

        response = self.client.post(self.update_url, {'status': 'in_delivery'})
        self.assertEqual(response.status_code, 302)

        self.available_order.refresh_from_db()
        self.assertEqual(self.available_order.status, 'in_delivery')

        response = self.client.post(self.update_url, {'status': 'delivered'})
        self.assertEqual(response.status_code, 302)

        self.available_order.refresh_from_db()
        self.assertEqual(self.available_order.status, 'delivered')

        response = self.client.get(self.orders_list_url)
        self.assertIn(self.available_order, response.context['finished_orders'])
        self.assertNotIn(self.available_order, response.context['active_orders'])
