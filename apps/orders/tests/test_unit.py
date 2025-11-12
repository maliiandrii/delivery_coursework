from django.test import TestCase
from apps.accounts.models import User
from apps.products.models import Product, Category
from apps.orders.models import Order, OrderItem


class OrderModelTests(TestCase):
    """Tests for order model"""

    def setUp(self):
        self.customer = User.objects.create_user(
            username='cust', password='pass123', user_type='customer'
        )
        self.courier = User.objects.create_user(
            username='cour', password='pass123', user_type='courier'
        )

        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Desc',
            price=10.00,
            category=self.category,
            stock=100
        )

        self.order = Order.objects.create(
            customer=self.customer,
            full_name='Test User',
            delivery_address='123 Main St',
            total_price=20.00
        )

    def test_order_creation(self):
        """Test order creation"""
        self.assertEqual(str(self.order), 'Order #55 - cust')
        self.assertEqual(self.order.status, 'pending')
        self.assertIsNone(self.order.courier)

    def test_assign_courier(self):
        """Test assigning a courier"""
        self.order.courier = self.courier
        self.order.save()
        self.assertEqual(self.order.courier, self.courier)

    def test_order_finished_status(self):
        """Test order finishing status"""
        self.assertFalse(self.order.is_finished())
        self.order.status = 'delivered'
        self.assertTrue(self.order.is_finished())
        self.order.status = 'cancelled'
        self.assertTrue(self.order.is_finished())

    def test_calculate_total(self):
        """Test calculating total price"""
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=10.00
        )
        self.order.calculate_total()
        self.assertEqual(self.order.total_price, 20.00)


class OrderItemModelTests(TestCase):
    """Tests for order item model"""

    def setUp(self):
        self.customer = User.objects.create_user(username='cust', password='pass')
        self.category = Category.objects.create(name='Test')
        self.product = Product.objects.create(
            name='Item', description='Test', price=15.00, category=self.category
        )
        self.order = Order.objects.create(
            customer=self.customer,
            full_name='Test',
            delivery_address='Addr'
        )

    def test_order_item_total(self):
        """Test calculating total price"""
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=3,
            price=15.00
        )
        self.assertEqual(item.get_total_price(), 45.00)
        self.assertEqual(str(item), '3x Item')
