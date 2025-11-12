from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.products.models import Product, Category
from decimal import Decimal


class ProductListViewTests(TestCase):
    """Tests for product list view functionality"""

    def setUp(self):
        self.client = Client()
        self.list_url = reverse('product_list')

        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic devices'
        )

        self.product1 = Product.objects.create(
            name='Product 1',
            description='Description 1',
            price=Decimal('99.99'),
            category=self.category,
            season='spring',
            size='medium',
            available=True
        )

        self.product2 = Product.objects.create(
            name='Product 2',
            description='Description 2',
            price=Decimal('149.99'),
            category=self.category,
            season='summer',
            size='large',
            available=True
        )

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

    def test_product_list_loads_for_anonymous(self):
        """Test product list loads for anonymous users"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_list.html')
        self.assertEqual(len(response.context['products']), 2)

    def test_product_list_loads_for_customer(self):
        """Test product list loads for customers"""
        self.client.force_login(self.customer)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Product 1')
        self.assertContains(response, 'Product 2')

    def test_product_list_redirects_courier(self):
        """Test couriers are redirected from product list"""
        self.client.force_login(self.courier)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('courier_orders'))

    def test_product_search_by_name(self):
        """Test product search functionality"""
        response = self.client.get(self.list_url, {'search': 'Product 1'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['products']), 1)
        self.assertEqual(response.context['products'][0].name, 'Product 1')

    def test_product_filter_by_category(self):
        """Test filtering products by category"""
        response = self.client.get(self.list_url, {'category': self.category.slug})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['products']), 2)

    def test_product_filter_by_season(self):
        """Test filtering products by season"""
        response = self.client.get(self.list_url, {'season': 'spring'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['products']), 1)
        self.assertEqual(response.context['products'][0].season, 'spring')

    def test_product_filter_by_size(self):
        """Test filtering products by size"""
        response = self.client.get(self.list_url, {'size': 'large'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['products']), 1)
        self.assertEqual(response.context['products'][0].size, 'large')

    def test_product_sort_by_price_asc(self):
        """Test sorting products by price ascending"""
        response = self.client.get(self.list_url, {'sort': 'price_asc'})

        self.assertEqual(response.status_code, 200)
        products = list(response.context['products'])
        self.assertEqual(products[0].price, Decimal('99.99'))
        self.assertEqual(products[1].price, Decimal('149.99'))

    def test_product_sort_by_price_desc(self):
        """Test sorting products by price descending"""
        response = self.client.get(self.list_url, {'sort': 'price_desc'})

        self.assertEqual(response.status_code, 200)
        products = list(response.context['products'])
        self.assertEqual(products[0].price, Decimal('149.99'))
        self.assertEqual(products[1].price, Decimal('99.99'))

    def test_product_unavailable_not_shown(self):
        """Test unavailable products are not displayed"""
        self.product1.available = False
        self.product1.save()

        response = self.client.get(self.list_url)
        self.assertEqual(len(response.context['products']), 1)


class ProductDetailViewTests(TestCase):
    """Tests for product detail view functionality"""

    def setUp(self):
        self.client = Client()

        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test Description',
            price=Decimal('99.99'),
            category=self.category,
            available=True
        )

        self.detail_url = reverse('product_detail', kwargs={'slug': self.product.slug})

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

    def test_product_detail_loads(self):
        """Test product detail page loads successfully"""
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_detail.html')
        self.assertContains(response, 'Test Product')
        self.assertContains(response, '$99.99')

    def test_product_detail_redirects_courier(self):
        """Test couriers are redirected from product detail"""
        self.client.force_login(self.courier)
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('courier_orders'))

    def test_product_detail_shows_related_products(self):
        """Test related products are shown"""
        related = Product.objects.create(
            name='Related Product',
            description='Related',
            price=Decimal('79.99'),
            category=self.category,
            available=True
        )

        response = self.client.get(self.detail_url)
        self.assertContains(response, 'Related Product')

    def test_product_detail_404_for_unavailable(self):
        """Test 404 for unavailable products"""
        self.product.available = False
        self.product.save()

        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 404)

    def test_product_detail_404_for_nonexistent(self):
        """Test 404 for non-existent products"""
        url = reverse('product_detail', kwargs={'slug': 'nonexistent'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
