from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User


class UserRegistrationTests(TestCase):
    """Tests for user registration functionality"""

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')

    def test_register_page_loads(self):
        """Test that register page loads successfully"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_register_customer_success(self):
        """Test successful customer registration"""
        data = {
            'username': 'testcustomer',
            'email': 'customer@test.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'user_type': 'customer',
            'phone': '+380501234567',
            'address': 'Test Address 123'
        }
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='testcustomer').exists())
        user = User.objects.get(username='testcustomer')
        self.assertEqual(user.user_type, 'customer')
        self.assertTrue(user.is_authenticated)

    def test_register_courier_success(self):
        """Test successful courier registration"""
        data = {
            'username': 'testcourier',
            'email': 'courier@test.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'user_type': 'courier'
        }
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='testcourier')
        self.assertEqual(user.user_type, 'courier')

    def test_register_password_mismatch(self):
        """Test registration fails with mismatched passwords"""
        data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'password1': 'TestPass123!',
            'password2': 'DifferentPass123!',
            'user_type': 'customer'
        }
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_register_duplicate_username(self):
        """Test registration fails with existing username"""
        User.objects.create_user(username='existing', password='pass123')

        data = {
            'username': 'existing',
            'email': 'new@test.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'user_type': 'customer'
        }
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username='existing').count(), 1)

    def test_register_redirect_if_authenticated(self):
        """Test authenticated users are redirected from register page"""
        user = User.objects.create_user(username='testuser', password='pass123')
        self.client.force_login(user)

        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 302)


class UserLoginTests(TestCase):
    """Tests for user login functionality"""

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
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

    def test_login_page_loads(self):
        """Test that login page loads successfully"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_login_customer_success(self):
        """Test successful customer login redirects to product list"""
        response = self.client.post(self.login_url, {
            'username': 'customer',
            'password': 'pass123'
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('product_list'))

    def test_login_courier_success(self):
        """Test successful courier login redirects to courier orders"""
        response = self.client.post(self.login_url, {
            'username': 'courier',
            'password': 'pass123'
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('courier_orders'))

    def test_login_invalid_credentials(self):
        """Test login fails with invalid credentials"""
        response = self.client.post(self.login_url, {
            'username': 'customer',
            'password': 'wrongpass'
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_redirect_if_authenticated(self):
        """Test authenticated users are redirected from login page"""
        self.client.force_login(self.customer)

        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 302)


class UserProfileTests(TestCase):
    """Tests for user profile functionality"""

    def setUp(self):
        self.client = Client()
        self.profile_url = reverse('profile')
        self.user = User.objects.create_user(
            username='testuser',
            password='pass123',
            email='test@test.com',
            user_type='customer'
        )

    def test_profile_requires_login(self):
        """Test profile page requires authentication"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_profile_page_loads_for_authenticated_user(self):
        """Test profile page loads for authenticated user"""
        self.client.force_login(self.user)
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        self.assertContains(response, 'testuser')

    def test_profile_update_success(self):
        """Test successful profile update"""
        self.client.force_login(self.user)

        data = {
            'username': 'testuser',
            'email': 'newemail@test.com',
            'phone': '+380501234567',
            'address': 'New Address 123'
        }
        response = self.client.post(self.profile_url, data)

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'newemail@test.com')
        self.assertEqual(self.user.phone, '+380501234567')
        self.assertEqual(self.user.address, 'New Address 123')

    def test_profile_update_invalid_email(self):
        """Test profile update fails with invalid email"""
        self.client.force_login(self.user)

        data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'phone': '+380501234567',
            'address': 'Test Address'
        }
        response = self.client.post(self.profile_url, data)

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'test@test.com')
