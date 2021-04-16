from django.contrib.auth import authenticate, get_user_model
from django.test import TestCase


User = get_user_model()


class CustomUserTest(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(
            username='test',
            email='test@example.com',
            password='foo'
        )
        self.assertEqual(authenticate(username='test', password='foo'), user)
        self.assertEqual(user.username, 'test')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_fail_user_create_if_email_is_empty(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(username='test', password='foo')
