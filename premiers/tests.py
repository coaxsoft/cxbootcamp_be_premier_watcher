from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from mixer.backend.django import mixer
from rest_framework.reverse import reverse
from rest_framework import status

from cxbootcamp_django_example.tests import BaseAPITest
from premiers.models import Premier, Comment, Vote
from premiers.utils import subquery_example


class TestPremierViewSet(BaseAPITest):

    def setUp(self) -> None:
        self.user = self.create_and_login()

        premier_at = timezone.now() + relativedelta(years=2)
        self.premier_happened = mixer.blend(Premier, is_active=True, premier_at=timezone.now())
        self.premier = mixer.blend(Premier, is_active=True, premier_at=premier_at)
        mixer.blend(Premier, is_active=False)

        self.data = {
            'name': 'Test',
            'description': 'Desc',
            'premier_at': timezone.now()
        }

    def test_list(self):
        resp = self.client.get(reverse('v1:premiers:premiers-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.assertEqual(len(resp.data['results']), 2)
        self.assertEqual(resp.data['results'][0]['id'], self.premier.id)
        self.assertTrue(resp.data['results'][0]['is_future'])

        self.assertFalse(resp.data['results'][1]['is_future'])

    def test_list_unauthorized(self):
        self.logout()

        resp = self.client.get(reverse('v1:premiers:premiers-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.assertEqual(len(resp.data['results']), 2)
        self.assertEqual(resp.data['results'][0]['id'], self.premier.id)

    def test_create(self):
        resp = self.client.post(reverse('v1:premiers:premiers-list'), data=self.data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        self.assertEqual(resp.data['name'], self.data['name'])
        self.assertEqual(resp.data['description'], self.data['description'])
        self.assertEqual(resp.data['premier_at'], self.data['premier_at'].isoformat().replace('+00:00', 'Z'))
        self.assertEqual(resp.data['user']['id'], self.user.id)

        p = Premier.objects.get(id=resp.data['id'])
        self.assertEqual(p.name, self.data['name'])
        self.assertEqual(p.description, self.data['description'])
        self.assertEqual(p.premier_at, self.data['premier_at'])
        self.assertEqual(p.user, self.user)

    def test_create_unauthorized(self):
        self.logout()
        resp = self.client.post(reverse('v1:premiers:premiers-list'), data=self.data)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_validation_error(self):
        self.data['premier_at'] = None
        resp = self.client.post(reverse('v1:premiers:premiers-list'), data=self.data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class TestSubquery(BaseAPITest):
    def setUp(self) -> None:
        self.user = self.create()
        self.premier = mixer.blend(Premier, is_active=True, premier_at=timezone.now())
        self.comment_zero = mixer.blend(Comment, premier=self.premier)
        self.comment_top = mixer.blend(Comment, premier=self.premier)

        ct = ContentType.objects.get_for_model(Comment)
        mixer.blend(Vote, user=self.user, content_type=ct, object_id=self.comment_zero.id, rating=-1)
        mixer.blend(Vote, user=self.user, content_type=ct, object_id=self.comment_top.id, rating=1)

    def test_top_comment(self):
        qs = subquery_example()
        self.assertEqual(qs.count(), 1)

        p: Premier = qs.first()
        self.assertEqual(p.top_comment_id, self.comment_top.id)
