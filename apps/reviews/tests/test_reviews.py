from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.orders.models import Order
from apps.reviews.models import Review
from decimal import Decimal


class ReviewListViewTests(TestCase):
    """Tests for review list view functionality"""

    def setUp(self):
        self.client = Client()
        self.list_url = reverse('review_list')

        self.customer = User.objects.create_user(
            username='customer',
            password='pass123',
            user_type='customer'
        )

        self.order = Order.objects.create(
            customer=self.customer,
            status='delivered',
            full_name='Test',
            delivery_address='Address',
            total_price=Decimal('100.00')
        )

        self.review = Review.objects.create(
            order=self.order,
            user=self.customer,
            rating=5,
            comment='Great service!'
        )

    def test_review_list_loads_for_anonymous(self):
        """Test review list loads for anonymous users"""
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reviews/review_list.html')
        self.assertContains(response, 'Great service!')

    def test_review_list_shows_all_reviews(self):
        """Test all reviews are displayed"""
        review2 = Review.objects.create(
            order=Order.objects.create(
                customer=self.customer,
                status='delivered',
                full_name='Test',
                delivery_address='Address',
                total_price=Decimal('50.00')
            ),
            user=self.customer,
            rating=4,
            comment='Good service'
        )

        response = self.client.get(self.list_url)
        self.assertEqual(len(response.context['reviews']), 2)

    def test_review_list_empty_state(self):
        """Test review list shows message when empty"""
        Review.objects.all().delete()

        response = self.client.get(self.list_url)
        self.assertContains(response, 'No reviews yet')


class CreateReviewTests(TestCase):
    """Tests for review creation functionality"""

    def setUp(self):
        self.client = Client()

        self.customer = User.objects.create_user(
            username='customer',
            password='pass123',
            user_type='customer'
        )

        self.other_customer = User.objects.create_user(
            username='other',
            password='pass123',
            user_type='customer'
        )

        self.delivered_order = Order.objects.create(
            customer=self.customer,
            status='delivered',
            full_name='Test',
            delivery_address='Address',
            total_price=Decimal('100.00')
        )

        self.pending_order = Order.objects.create(
            customer=self.customer,
            status='pending',
            full_name='Test',
            delivery_address='Address',
            total_price=Decimal('50.00')
        )

        self.review_url = reverse('create_review', kwargs={'order_id': self.delivered_order.id})

    def test_create_review_requires_login(self):
        """Test review creation requires authentication"""
        response = self.client.post(self.review_url, {
            'rating': 5,
            'comment': 'Great!'
        })
        self.assertEqual(response.status_code, 302)

    def test_create_review_success(self):
        """Test successful review creation"""
        self.client.force_login(self.customer)

        data = {
            'rating': 5,
            'comment': 'Excellent service!'
        }

        response = self.client.post(self.review_url, data)
        self.assertEqual(response.status_code, 302)

        self.assertTrue(Review.objects.filter(order=self.delivered_order).exists())
        review = Review.objects.get(order=self.delivered_order)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Excellent service!')

    def test_create_review_for_pending_order_fails(self):
        """Test cannot review pending orders"""
        url = reverse('create_review', kwargs={'order_id': self.pending_order.id})
        self.client.force_login(self.customer)

        data = {
            'rating': 5,
            'comment': 'Great!'
        }

        response = self.client.post(url, data)
        self.assertFalse(Review.objects.filter(order=self.pending_order).exists())

    def test_create_duplicate_review_fails(self):
        """Test cannot create duplicate review"""
        Review.objects.create(
            order=self.delivered_order,
            user=self.customer,
            rating=5,
            comment='First review'
        )

        self.client.force_login(self.customer)

        data = {
            'rating': 4,
            'comment': 'Second review'
        }

        response = self.client.post(self.review_url, data)
        self.assertEqual(Review.objects.filter(order=self.delivered_order).count(), 1)

    def test_create_review_other_user_order_fails(self):
        """Test users cannot review other users' orders"""
        self.client.force_login(self.other_customer)

        data = {
            'rating': 5,
            'comment': 'Great!'
        }

        response = self.client.post(self.review_url, data)
        self.assertEqual(response.status_code, 404)

    def test_create_review_invalid_rating(self):
        """Test review with invalid rating fails"""
        self.client.force_login(self.customer)

        data = {
            'rating': 6,
            'comment': 'Great!'
        }

        response = self.client.post(self.review_url, data)
        self.assertFalse(Review.objects.filter(order=self.delivered_order).exists())

    def test_create_review_missing_comment(self):
        """Test review without comment fails"""
        self.client.force_login(self.customer)

        data = {
            'rating': 5,
            'comment': ''
        }

        response = self.client.post(self.review_url, data)
        self.assertFalse(Review.objects.filter(order=self.delivered_order).exists())
