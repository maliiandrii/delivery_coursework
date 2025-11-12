from django.test import TestCase
from apps.accounts.models import User
from apps.orders.models import Order
from apps.reviews.models import Review
from apps.products.models import Category, Product
from apps.reviews.forms import ReviewForm


class ReviewModelTests(TestCase):
    """Tests for review model"""

    def setUp(self):
        self.user = User.objects.create_user(username='reviewer', password='pass123')
        self.category = Category.objects.create(name='Test')
        self.product = Product.objects.create(
            name='Test', description='Desc', price=10.00, category=self.category
        )
        self.order = Order.objects.create(
            customer=self.user,
            full_name='Reviewer',
            delivery_address='123 Review St',
            status='delivered'
        )

    def test_review_creation(self):
        """Test for review creation"""
        review = Review.objects.create(
            order=self.order,
            user=self.user,
            rating=5,
            comment='Great service!'
        )
        self.assertEqual(str(review), 'Review by reviewer - 5 stars')
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.order.review, review)


class ReviewFormTests(TestCase):
    """Tests for review form class"""

    def test_valid_form(self):
        """Test for valid form"""
        form_data = {'rating': 4, 'comment': 'Good job!'}
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_rating(self):
        """Test for invalid rating"""
        form_data = {'rating': 6, 'comment': 'Too high!'}
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)
