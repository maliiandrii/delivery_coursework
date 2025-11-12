from django.test import TestCase
from apps.accounts.models import User
from apps.accounts.forms import UserRegistrationForm, UserLoginForm, UserProfileForm


class UserModelTests(TestCase):
    """Tests for User model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='customer',
            phone='+380991234567',
            address='123 Test St'
        )

    def test_user_creation(self):
        """Test user creation"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertEqual(self.user.user_type, 'customer')
        self.assertEqual(str(self.user), 'testuser (Customer)')

    def test_user_type_methods(self):
        """Test user type methods"""
        self.assertTrue(self.user.is_customer())
        self.assertFalse(self.user.is_courier())

        self.user.user_type = 'courier'
        self.user.save()

        self.assertTrue(self.user.is_courier())
        self.assertFalse(self.user.is_customer())


class LoginFormTests(TestCase):
    """Tests for login form"""

    def test_login_form_fields(self):
        """Test login form fields"""
        form = UserLoginForm()
        self.assertIn('class="form-input"', form['username'].as_widget())
        self.assertIn('class="form-input"', form['password'].as_widget())


class UserProfileFormTests(TestCase):
    """Tests for user profile form"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='profileuser',
            email='profile@test.com',
            phone='1234567890',
            address='Profile St'
        )

    def test_profile_form_saves_changes(self):
        """Test profile form saves changes"""
        form_data = {
            'username': 'updateduser',
            'email': 'updated@test.com',
            'phone': '0987654321',
            'address': 'New Address'
        }
        form = UserProfileForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())
        updated_user = form.save()
        self.assertEqual(updated_user.username, 'updateduser')
        self.assertEqual(updated_user.email, 'updated@test.com')


class UserRegistrationFormTests(TestCase):
    """Tests for User registration form."""

    def test_form_valid_data(self):
        """Test form is valid"""
        form_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'phone': '+380991112233',
            'address': '456 Test Ave',
            'user_type': 'courier',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_missing_required_fields(self):
        """Test form is invalid"""
        form_data = {
            'username': '',
            'email': '',
            'password1': 'pass',
            'password2': 'pass2',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('password2', form.errors)

    def test_form_save_creates_user(self):
        """Test form is valid and creates user"""
        form_data = {
            'username': 'formuser',
            'email': 'form@example.com',
            'password1': 'FormPass123!',
            'password2': 'FormPass123!',
            'user_type': 'customer',
            'phone': '1234567890',
            'address': '789 Form St',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, 'formuser')
        self.assertEqual(user.user_type, 'customer')
