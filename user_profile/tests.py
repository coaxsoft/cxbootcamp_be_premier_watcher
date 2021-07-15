from django.contrib.auth.hashers import check_password
from unittest.mock import patch
from rest_framework.reverse import reverse
from cxbootcamp_django_example.tests import BaseAPITest


class TestProfileViewSet(BaseAPITest):

    def setUp(self):
        self.password = 'test_password'
        self.user = self.create_and_login(password=self.password)
        self.data = {
            "email": "new@email.com",
        }

    def test_get_profile(self):
        resp = self.client.get(reverse('v1:user_profile:profile'))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['id'], self.user.id)
        self.assertEqual(resp.data['email'], self.user.email)

    def test_get_profile_unauthorized(self):
        self.logout()
        resp = self.client.get(reverse('v1:user_profile:profile'))

        self.assertEqual(resp.status_code, 401)

    @patch('notifications.tasks.send_email.delay')
    def test_change_password(self, delay):
        data = {
            "old_password": self.password,
            "password": "new_pass!",
        }
        resp = self.client.post(reverse('v1:user_profile:password-change'), data=data)
        self.user.refresh_from_db()
        self.assertEqual(resp.status_code, 204)
        self.assertTrue(check_password(data['password'], self.user.password))
        delay.assert_called_once()

    def test_change_password_wrong_old_password(self):
        data = {
            "old_password": self.password + 'some_str',
            "password": "new_pass!"
        }
        resp = self.client.post(reverse('v1:user_profile:password-change'), data=data)
        self.user.refresh_from_db()
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(check_password(data['password'], self.user.password))

    @patch('notifications.tasks.send_email.delay')
    def test_deactivate_user_profile(self, send_email_task):
        resp = self.client.post(reverse('v1:user_profile:deactivate'))
        self.assertEqual(resp.status_code, 204)

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        send_email_task.assert_called_once()

    @patch('notifications.tasks.send_email.delay')
    def test_change_email(self, send_email_task):
        data = {
            "email": "test442@mail.com",
            "path": "change/email",
        }
        resp = self.client.patch(reverse('v1:user_profile:email'), data=data)
        self.user.refresh_from_db()
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(self.user.is_active)
        self.assertEqual(self.user.email, data['email'])
        self.assertEqual(resp.data['email'], data['email'])
        send_email_task.assert_called_once()

    def test_email_already_exists(self):
        data = {
            "email": "new@email.com",
        }
        self.create(email=data['email'])
        resp = self.client.patch(reverse('v1:user_profile:email'), data=data)
        self.user.refresh_from_db()
        self.assertEqual(resp.status_code, 400)
        self.assertNotEqual(self.user.email, data['email'])

    def test_email_uppercase_already_exists(self):
        email = "test453211@mail.com"
        self.create(email=email)
        resp = self.client.patch(reverse('v1:user_profile:email'), data={"email": email.upper()})
        self.assertEqual(resp.status_code, 400)

        self.user.refresh_from_db()
        self.assertNotEqual(self.user.email, email)
