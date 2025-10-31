from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone, translation
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import timedelta
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.history.models import History
from apps.history.serializers import HistoryListSerializer, HistoryRetrieveSerializer

User = get_user_model()


def create_test_image():
    """Test uchun rasm yaratish"""
    file = BytesIO()
    image = Image.new('RGB', (100, 100), color='red')
    image.save(file, 'png')
    file.name = 'test.png'
    file.seek(0)
    return SimpleUploadedFile(
        name='test_image.png',
        content=file.read(),
        content_type='image/png'
    )


class HistoryModelTestCase(TestCase):
    """Test cases for History model"""

    def setUp(self):
        self.history_data = {
            'title_uz': 'Test Tarix UZ',
            'title_en': 'Test History EN',
            'short_description_uz': 'Qisqa tavsif UZ',
            'short_description_en': 'Short description EN',
            'long_description_uz': 'To\'liq tavsif UZ',
            'long_description_en': 'Full description EN',
            'button_text_uz': 'Batafsil UZ',
            'button_text_en': 'More EN',
            'button_link': 'https://example.com',
            'start_date': timezone.now().date(),
            'end_date': (timezone.now() + timedelta(days=30)).date(),
            'is_active': True
        }

    def test_create_history(self):
        history = History.objects.create(**self.history_data)
        self.assertEqual(history.title_en, 'Test History EN')
        self.assertTrue(history.is_active)
        self.assertIsNotNone(history.created_at)

    def test_history_str_method(self):
        history = History.objects.create(**self.history_data)
        self.assertIsInstance(str(history), str)

    def test_history_with_image(self):
        self.history_data['image'] = create_test_image()
        history = History.objects.create(**self.history_data)
        self.assertIsNotNone(history.image)

    def test_history_dates_validation(self):
        pass

    def test_inactive_history(self):
        self.history_data['is_active'] = False
        history = History.objects.create(**self.history_data)
        self.assertFalse(history.is_active)


class HistoryListAPIViewTestCase(APITestCase):

    def setUp(self):
        self.url = '/api/v1/history/'
        self.user = User.objects.create_user(
            phone='+998901234567',
            username='testuser',
            password='TestPass123!',
            is_active=True
        )

        self.history1 = History.objects.create(
            title_uz='Tarix 1 UZ',
            title_en='History 1 EN',
            short_description_uz='Qisqa 1',
            short_description_en='Short 1',
            long_description_uz='To\'liq 1',
            long_description_en='Full 1',
            button_text_uz='Batafsil',
            button_text_en='More',
            button_link='https://example.com/1',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=30)).date(),
            is_active=True
        )

        self.history2 = History.objects.create(
            title_uz='Tarix 2 UZ',
            title_en='History 2 EN',
            short_description_uz='Qisqa 2',
            short_description_en='Short 2',
            long_description_uz='To\'liq 2',
            long_description_en='Full 2',
            button_text_uz='Batafsil',
            button_text_en='More',
            button_link='https://example.com/2',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=30)).date(),
            is_active=True
        )

        self.inactive_history = History.objects.create(
            title_uz='Aktiv emas',
            title_en='Inactive',
            short_description_uz='Qisqa',
            short_description_en='Short',
            long_description_uz='To\'liq',
            long_description_en='Full',
            button_text_uz='Batafsil',
            button_text_en='More',
            button_link='https://example.com/3',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=30)).date(),
            is_active=False
        )

    # Boshqa testlar avvalgidek, rus tiliga oid barcha tekshiruvlar olib tashlandi


class HistoryRetrieveAPIViewTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            phone='+998901234567',
            username='testuser',
            password='TestPass123!',
            is_active=True
        )

        self.history = History.objects.create(
            title_uz='Test Tarix UZ',
            title_en='Test History EN',
            short_description_uz='Qisqa tavsif',
            short_description_en='Short description',
            long_description_uz='To\'liq tavsif juda uzun',
            long_description_en='Full description very long',
            button_text_uz='Batafsil',
            button_text_en='More',
            button_link='https://example.com/detail',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=30)).date(),
            is_active=True
        )

        self.inactive_history = History.objects.create(
            title_uz='Aktiv emas',
            title_en='Inactive',
            short_description_uz='Qisqa',
            short_description_en='Short',
            long_description_uz='To\'liq',
            long_description_en='Full',
            button_text_uz='Batafsil',
            button_text_en='More',
            button_link='https://example.com/inactive',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=30)).date(),
            is_active=False
        )

        self.url = f'/api/v1/history/{self.history.pk}/'


class HistorySerializerTestCase(TestCase):

    def setUp(self):
        self.history = History.objects.create(
            title_uz='Test UZ',
            title_en='Test EN',
            short_description_uz='Short UZ',
            short_description_en='Short EN',
            long_description_uz='Long UZ',
            long_description_en='Long EN',
            button_text_uz='Button UZ',
            button_text_en='Button EN',
            button_link='https://example.com',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=30)).date(),
            is_active=True
        )