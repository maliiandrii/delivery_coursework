from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.orders.models import Order
from decimal import Decimal


class CourierOrdersViewTests(TestCase):
    """Tests for courier orders view functionality"""

    def setUp(self):
        self.client = Client()
        self.orders_url = reverse('courier_orders')

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

        self.other_courier = User.objects.create_user(
            username='other_courier',
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

        self.active_order = Order.objects.create(
            customer=self.customer,
            courier=self.courier,
            status='confirmed',
            full_name='Test',
            delivery_address='Address',
            total_price=Decimal('150.00')
        )

        self.finished_order = Order.objects.create(
            customer=self.customer,
            courier=self.courier,
            status='delivered',
            full_name='Test',
            delivery_address='Address',
            total_price=Decimal('200.00')
        )

    def test_courier_orders_requires_login(self):
        """Test courier orders requires authentication"""
        response = self.client.get(self.orders_url)
        self.assertEqual(response.status_code, 302)

    def test_courier_orders_customer_denied(self):
        """Test customers cannot access courier orders"""
        self.client.force_login(self.customer)
        response = self.client.get(self.orders_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('product_list'))

    def test_courier_orders_loads_for_courier(self):
        """Test courier orders page loads for couriers"""
        self.client.force_login(self.courier)
        response = self.client.get(self.orders_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courier/courier_orders.html')

    def test_courier_sees_available_orders(self):
        """Test courier sees available orders"""
        self.client.force_login(self.courier)
        response = self.client.get(self.orders_url)

        available_orders = response.context['available_orders']
        self.assertEqual(len(available_orders), 1)
        self.assertEqual(available_orders[0].id, self.available_order.id)

    def test_courier_sees_own_active_orders(self):
        """Test courier sees their own active orders"""
        self.client.force_login(self.courier)
        response = self.client.get(self.orders_url)

        active_orders = response.context['active_orders']
        self.assertEqual(len(active_orders), 1)
        self.assertEqual(active_orders[0].id, self.active_order.id)

    def test_courier_sees_own_finished_orders(self):
        """Test courier sees their own finished orders"""
        self.client.force_login(self.courier)
        response = self.client.get(self.orders_url)

        finished_orders = response.context['finished_orders']
        self.assertEqual(len(finished_orders), 1)
        self.assertEqual(finished_orders[0].id, self.finished_order.id)

    def test_courier_doesnt_see_other_courier_orders(self):
        """Test courier doesn't see other couriers' orders"""
        other_order = Order.objects.create(
            customer=self.customer,
            courier=self.other_courier,
            status='confirmed',
            full_name='Test',
            delivery_address='Address',
            total_price=Decimal('100.00')
        )

        self.client.force_login(self.courier)
        response = self.client.get(self.orders_url)

        active_orders = response.context['active_orders']
        self.assertNotIn(other_order, active_orders)


class AcceptOrderTests(TestCase):
    """Tests for order acceptance functionality"""

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

        self.accept_url = reverse('accept_order', kwargs={'order_id': self.order.id})

    def test_accept_order_requires_login(self):
        """Test accepting order requires authentication"""
        response = self.client.post(self.accept_url)
        self.assertEqual(response.status_code, 302)

    def test_accept_order_customer_denied(self):
        """Test customers cannot accept orders"""
        self.client.force_login(self.customer)
        response = self.client.post(self.accept_url)

        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertIsNone(self.order.courier)
        self.assertEqual(self.order.status, 'pending')

    def test_accept_order_success(self):
        """Test successful order acceptance"""
        self.client.force_login(self.courier)
        response = self.client.post(self.accept_url)

        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.courier, self.courier)
        self.assertEqual(self.order.status, 'confirmed')

    def test_accept_already_assigned_order_fails(self):
        """Test cannot accept already assigned order"""
        other_courier = User.objects.create_user(
            username='other',
            password='pass123',
            user_type='courier'
        )

        self.order.courier = other_courier
        self.order.status = 'confirmed'
        self.order.save()

        self.client.force_login(self.courier)
        response = self.client.post(self.accept_url)

        self.assertEqual(response.status_code, 404)
        self.order.refresh_from_db()
        self.assertEqual(self.order.courier, other_courier)


class UpdateOrderStatusTests(TestCase):
    """Tests for order status update functionality"""

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

        self.other_courier = User.objects.create_user(
            username='other',
            password='pass123',
            user_type='courier'
        )

        self.order = Order.objects.create(
            customer=self.customer,
            courier=self.courier,
            status='confirmed',
            full_name='Test',
            delivery_address='Address',
            total_price=Decimal('100.00')
        )

        self.update_url = reverse('update_order_status', kwargs={'order_id': self.order.id})

    def test_update_status_requires_login(self):
        """Test updating status requires authentication"""
        response = self.client.post(self.update_url, {'status': 'in_delivery'})
        self.assertEqual(response.status_code, 302)

    def test_update_status_customer_denied(self):
        """Test customers cannot update order status"""
        self.client.force_login(self.customer)
        response = self.client.post(self.update_url, {'status': 'in_delivery'})

        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'confirmed')

    def test_update_status_success(self):
        """Test successful status update"""
        self.client.force_login(self.courier)
        response = self.client.post(self.update_url, {'status': 'in_delivery'})

        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'in_delivery')

    def test_update_status_to_delivered(self):
        """Test updating status to delivered"""
        self.client.force_login(self.courier)
        response = self.client.post(self.update_url, {'status': 'delivered'})

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'delivered')

    def test_update_delivered_order_fails(self):
        """Test cannot update delivered order status"""
        self.order.status = 'delivered'
        self.order.save()

        self.client.force_login(self.courier)
        response = self.client.post(self.update_url, {'status': 'confirmed'})

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'delivered')

    def test_update_cancelled_order_fails(self):
        """Test cannot update cancelled order status"""
        self.order.status = 'cancelled'
        self.order.save()

        self.client.force_login(self.courier)
        response = self.client.post(self.update_url, {'status': 'confirmed'})

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'cancelled')

    def test_update_other_courier_order_fails(self):
        """Test courier cannot update other courier's orders"""
        self.client.force_login(self.other_courier)
        response = self.client.post(self.update_url, {'status': 'in_delivery'})

        self.assertEqual(response.status_code, 404)

    def test_update_invalid_status_fails(self):
        """Test updating to invalid status fails"""
        self.client.force_login(self.courier)
        response = self.client.post(self.update_url, {'status': 'invalid_status'})

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'confirmed')
