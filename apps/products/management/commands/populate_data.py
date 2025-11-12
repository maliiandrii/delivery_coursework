"""
Management command to populate database with sample data.
Usage: python manage.py populate_data
"""

from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.products.models import Category, Product
from decimal import Decimal


class Command(BaseCommand):
    """Command to populate database with sample data for testing"""

    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')

        categories_data = [
            {'name': 'Electronics', 'description': 'Electronic devices and gadgets'},
            {'name': 'Clothing', 'description': 'Fashion and apparel'},
            {'name': 'Food', 'description': 'Food and beverages'},
            {'name': 'Books', 'description': 'Books and magazines'},
            {'name': 'Home & Garden', 'description': 'Home improvement and gardening'},
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')

        products_data = [
            {
                'name': 'Wireless Headphones',
                'description': 'High-quality wireless headphones with noise cancellation',
                'price': Decimal('89.99'),
                'category': categories[0],
                'season': 'spring',
                'size': 'medium',
                'stock': 50
            },
            {
                'name': 'Smart Watch',
                'description': 'Fitness tracker with heart rate monitor',
                'price': Decimal('199.99'),
                'category': categories[0],
                'season': 'summer',
                'size': 'small',
                'stock': 30
            },
            {
                'name': 'Winter Jacket',
                'description': 'Warm and stylish winter jacket',
                'price': Decimal('129.99'),
                'category': categories[1],
                'season': 'winter',
                'size': 'large',
                'stock': 25
            },
            {
                'name': 'Summer T-Shirt',
                'description': 'Comfortable cotton t-shirt',
                'price': Decimal('19.99'),
                'category': categories[1],
                'season': 'summer',
                'size': 'medium',
                'stock': 100
            },
            {
                'name': 'Organic Coffee',
                'description': 'Premium organic coffee beans',
                'price': Decimal('15.99'),
                'category': categories[2],
                'season': 'autumn',
                'size': 'small',
                'stock': 75
            },
            {
                'name': 'Cooking Book',
                'description': 'Professional cooking recipes',
                'price': Decimal('29.99'),
                'category': categories[3],
                'stock': 40
            },
            {
                'name': 'Garden Tools Set',
                'description': 'Complete set of gardening tools',
                'price': Decimal('79.99'),
                'category': categories[4],
                'season': 'spring',
                'size': 'large',
                'stock': 20
            },
            {
                'name': 'LED Lamp',
                'description': 'Energy-efficient LED desk lamp',
                'price': Decimal('34.99'),
                'category': categories[4],
                'stock': 60
            },
        ]

        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults=prod_data
            )
            if created:
                self.stdout.write(f'Created product: {product.name}')

        test_users = [
            {
                'username': 'customer1',
                'email': 'customer1@example.com',
                'password': 'password123',
                'user_type': 'customer',
                'phone': '+380501234567',
                'address': 'Kyiv, Khreshchatyk 1'
            },
            {
                'username': 'courier1',
                'email': 'courier1@example.com',
                'password': 'password123',
                'user_type': 'courier',
                'phone': '+380507654321',
            },
        ]

        for user_data in test_users:
            password = user_data.pop('password')
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(f'Created user: {user.username} ({user.user_type})')

        self.stdout.write(self.style.SUCCESS('Successfully populated database!'))
        self.stdout.write('')
        self.stdout.write('Test accounts:')
        self.stdout.write('  Customer: username=customer1, password=password123')
        self.stdout.write('  Courier: username=courier1, password=password123')
