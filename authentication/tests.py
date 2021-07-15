from django.contrib.auth.hashers import check_password

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from rest_framework.reverse import reverse
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from unittest.mock import patch

from authentication.models import User
from authentication.tokens import TokenGenerator
from cxbootcamp_django_example.tests import BaseAPITest


class TestObtainJSONWebTokenView(BaseAPITest):

    def setUp(self):
        self.email = "test@mail.com"
        self.password = "test_password"
        self.user = self.create(email=self.email, password=self.password)

    def test_get_token_pair(self):
        resp = self.client.post(reverse('v1:auth:auth'), data={'email': self.email, 'password': self.password})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('refresh', resp.data)
        self.assertIn('access', resp.data)

    def test_get_token_authentication_error(self):
        resp = self.client.post(reverse('v1:auth:auth'), data={'email': 'fake_data', 'password': 'fake_data'})
        self.assertEqual(resp.status_code, 401)


class TestVerifyJSONWebTokenView(BaseAPITest):

    def setUp(self):
        self.email = "test@mail.com"
        self.password = "test_password"
        self.user = self.create(email=self.email, password=self.password)
        self.access_token = str(AccessToken.for_user(self.user))

    def test_token_is_valid(self):
        resp = self.client.post(reverse('v1:auth:auth-verify'), data={'token': self.access_token})
        self.assertEqual(resp.status_code, 200)

    def test_get_token_validation_error(self):
        resp = self.client.post(reverse('v1:auth:auth-verify'), data={'token': 'fake_data'})
        self.assertEqual(resp.status_code, 401)


class TestRefreshJSONWebTokenView(BaseAPITest):

    def setUp(self):
        self.email = "test@mail.com"
        self.password = "test_password"
        self.user = self.create(email=self.email, password=self.password)
        self.refresh_token = str(RefreshToken.for_user(self.user))

    def test_get_access_token(self):
        resp = self.client.post(reverse('v1:auth:auth-refresh'), data={'refresh': self.refresh_token})
        self.assertIn('access', resp.data)

    def test_get_token_refresh_error(self):
        resp = self.client.post(reverse('v1:auth:auth-refresh'), data={'refresh': 'fake_data'})
        self.assertEqual(resp.status_code, 401)


class TestSignUpView(BaseAPITest):

    def setUp(self):
        self.data = {
            "email": "test@test.com",
            "password": "testpassword123",
            "path": "/activate/",
        }

    @patch('notifications.tasks.send_email.delay')
    def test_sign_up(self, email_delay):
        resp = self.client.post(reverse('v1:auth:sign-up'), data=self.data)

        self.assertEqual(resp.status_code, 201)
        self.assertTrue(User.objects.filter(email=self.data['email']).exists())
        email_delay.assert_called_once()

    @patch('notifications.tasks.send_email.delay')
    def test_sign_up_email_to_lower_case(self, email_delay):
        self.data['email'] = 'CAPs@mail.com'
        resp = self.client.post(reverse('v1:auth:sign-up'), data=self.data)

        self.assertEqual(resp.status_code, 201)
        self.assertTrue(User.objects.filter(email=self.data['email'].lower(),).exists())
        email_delay.assert_called_once()

    def test_sign_up_user_exists(self):
        email = 'test@test.com'
        self.create(email=email)
        self.data['email'] = email
        resp = self.client.post(reverse('v1:auth:sign-up'), data=self.data)
        self.assertEqual(resp.status_code, 400)


class TestActivateUserView(BaseAPITest):

    def setUp(self):
        self.user = self.create('test@email.com', 'qwerty12345')
        self.user.is_active = False
        self.user.save()

    def test_user_activation(self):
        token = f"{urlsafe_base64_encode(force_bytes(self.user.email))}.{TokenGenerator.make_token(self.user)}"
        resp = self.client.post(reverse('v1:auth:activate'), data={'token': token})
        self.assertEqual(resp.status_code, 200)
        user = User.objects.get(pk=self.user.pk)
        self.assertTrue(user.is_active)
        self.assertTrue('access' in resp.data.keys())
        self.assertTrue('refresh' in resp.data.keys())

    def test_user_activation_wrong_uid(self):
        token = f"rewrewviurehgfuyeryu.{TokenGenerator.make_token(self.user)}"
        resp = self.client.post(reverse('v1:auth:activate'), data={'token': token})
        self.assertEqual(resp.status_code, 400)

    def test_user_activation_wrong_token(self):
        token = f"{urlsafe_base64_encode(force_bytes(self.user.email))}.rewrewrewfewfewf"
        resp = self.client.post(reverse('v1:auth:activate'), data={'token': token})
        self.assertEqual(resp.status_code, 400)

    def test_user_activation_user_does_not_exists(self):
        token = f"{urlsafe_base64_encode(force_bytes('wrong@email.com'))}.{TokenGenerator.make_token(self.user)}"
        resp = self.client.post(reverse('v1:auth:activate'), data={'token': token})
        self.assertEqual(resp.status_code, 400)


class TestPasswordReset(BaseAPITest):

    def setUp(self):
        self.data = {
            "email": "test@mail.com",
            "path": "restore/password",
        }
        self.user = self.create_and_login(email=self.data['email'])

    @patch('notifications.tasks.send_email.delay')
    def test_forget_password(self, send_email_task):
        resp = self.client.post(reverse('v1:auth:reset'), data=self.data)
        self.assertEqual(resp.status_code, 204)
        send_email_task.assert_called_once()

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_restoring_password)

    def test_forget_password_wrong_email(self):
        self.data['email'] = '_wrong'
        resp = self.client.post(reverse('v1:auth:reset'), data=self.data)
        self.assertEqual(resp.status_code, 400)

    def test_forget_password_user_does_not_exists(self):
        self.data['email'] = 'nonexistemail@mail.com'
        resp = self.client.post(reverse('v1:auth:reset'), data=self.data)
        self.assertEqual(resp.status_code, 400)


class TestPasswordRestore(BaseAPITest):

    def setUp(self):
        self.user = self.create_and_login()
        self.user.is_restoring_password = True
        self.user.save()

        self.data = {
            "token": f"{urlsafe_base64_encode(force_bytes(self.user.email))}.{TokenGenerator.make_token(self.user)}",
            "password": "new_shiny_password",
        }

    def test_reset_password(self):
        resp = self.client.post(reverse('v1:auth:restore'), data=self.data)
        self.assertEqual(resp.status_code, 204)
        self.user.refresh_from_db()
        self.assertTrue(check_password(self.data['password'], self.user.password))
        self.assertFalse(self.user.is_restoring_password)

    def test_reset_password_invalid_token(self):
        self.data['token'] += '_wrong'
        resp = self.client.post(reverse('v1:auth:restore'), data=self.data)
        self.assertEqual(resp.status_code, 400)

    def test_reset_password_wrong_email(self):
        self.data['token'] = f"{urlsafe_base64_encode(force_bytes('1@2.ua'))}." \
                             f"{TokenGenerator.make_token(self.user)}"
        resp = self.client.post(reverse('v1:auth:restore'), data=self.data)
        self.assertEqual(resp.status_code, 400)

    def test_restore_restoring_password_false(self):
        self.user.is_restoring_password = False
        self.user.save()
        resp = self.client.post(reverse('v1:auth:restore'), data=self.data)
        self.assertEqual(resp.status_code, 400)
