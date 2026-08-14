from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(
    SECURE_SSL_REDIRECT=False,
    STORAGES={
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    },
)
class VisitorStatsAccessTests(TestCase):
    """`/stats/` exposes visitor IPs and geolocation — must not be public."""

    def setUp(self):
        self.url = reverse('visitor_stats')
        self.password = 'test-pass-123'
        self.user = User.objects.create_user(
            username='visitor',
            password=self.password,
        )
        self.staff = User.objects.create_user(
            username='staffer',
            password=self.password,
            is_staff=True,
        )

    def test_anonymous_cannot_view_stats(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)

    def test_non_staff_cannot_view_stats(self):
        self.client.login(username='visitor', password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)

    def test_staff_can_view_stats(self):
        self.client.login(username='staffer', password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
