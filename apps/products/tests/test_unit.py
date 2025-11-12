from django.test import TestCase
from apps.products.models import Product, Category


class CategoryModelTests(TestCase):
    """Tests for category model"""

    def test_category_slug_creation(self):
        """Test category slug creation"""
        category = Category.objects.create(name='Spring Flowers')
        self.assertEqual(category.slug, 'spring-flowers')
        self.assertEqual(str(category), 'Spring Flowers')


class ProductModelTests(TestCase):
    """Tests for product model"""

    def setUp(self):
        self.category = Category.objects.create(name='Test Category')

    def test_product_slug_and_str(self):
        """Test product slug and product str"""
        product = Product.objects.create(
            name='Red Roses',
            description='Beautiful red roses',
            price=25.00,
            category=self.category,
            stock=50
        )
        self.assertEqual(product.slug, 'red-roses')
        self.assertEqual(str(product), 'Red Roses')

    def test_product_season_and_size_choices(self):
        """Test product season choices and size"""
        product = Product.objects.create(
            name='Summer Bouquet',
            description='For hot days',
            price=30.00,
            category=self.category,
            season='summer',
            size='large'
        )
        self.assertEqual(product.season, 'summer')
        self.assertEqual(product.size, 'large')
