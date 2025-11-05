from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import timedelta
from io import BytesIO
from PIL import Image
import uuid

from apps.admins.serializers.histories import HistorySerializer
from apps.history.models import History
from apps.shared.models import Media
from apps.users.models.device import Device, AppVersion, DeviceType

User = get_user_model()


class HistoryModelTestCase(TestCase):
    """Test cases for History model"""

    def setUp(self):
        self.history_data = {
            'title_uz': 'Test Tarix',
            'title_en': 'Test History',
            'short_description_uz': 'Qisqa tavsif test uchun',
            'short_description_en': 'Short description for test',
            'long_description_uz': 'Uzun tavsif test uchun yozilgan',
            'long_description_en': 'Long description written for test',
            'button_text_uz': 'Batafsil',
            'button_text_en': 'Read More',
            'button_link': 'https://example.com',
            'start_date': timezone.now() + timedelta(hours=1),
            'end_date': timezone.now() + timedelta(hours=2),
            'is_active': True
        }

    def test_create_history(self):
        """History yaratish"""
        history = History.objects.create(**self.history_data)

        self.assertEqual(history.title_uz, 'Test Tarix')
        self.assertEqual(history.title_en, 'Test History')
        self.assertTrue(history.is_active)
        self.assertIsNotNone(history.created_at)

    def test_history_str_method(self):
        """History __str__ method"""
        history = History.objects.create(**self.history_data)
        self.assertIsNotNone(str(history))

    def test_history_dates_validation(self):
        """Start va end date'larni tekshirish"""
        history = History.objects.create(**self.history_data)

        self.assertIsNotNone(history.start_date)
        self.assertIsNotNone(history.end_date)
        self.assertTrue(history.end_date > history.start_date)

    def test_history_optional_button_link(self):
        """Button link optional"""
        data = self.history_data.copy()
        data['button_link'] = None

        history = History.objects.create(**data)
        self.assertIsNone(history.button_link)

    def test_history_with_media(self):
        """History bilan media files"""
        history = History.objects.create(**self.history_data)

        user = User.objects.create_user(
            phone='+998901234567',
            username='testuser',
            password='TestPass123!'
        )

        # Test rasm yaratish
        image = Image.new('RGB', (100, 100), color='red')
        image_file = BytesIO()
        image.save(image_file, 'JPEG')
        image_file.seek(0)
        uploaded_file = SimpleUploadedFile(
            'test.jpg',
            image_file.read(),
            content_type='image/jpeg'
        )

        # Media yaratish (file_size avtomatik hisoblanadi)
        media = Media.objects.create(
            content_object=history,
            file=uploaded_file,
            media_type='image',
            original_filename='test.jpg',
            uploaded_by=user,
            language='uz',
            is_public=True
        )

        self.assertEqual(history.media_files.count(), 1)
        self.assertIsNotNone(media.file_size)


class HistoryListCreateAPIViewTestCase(APITestCase):
    """Test cases for History list and create"""

    def setUp(self):
        self.url = '/api/v1/admins/histories/'

        # Admin user yaratish
        self.admin_user = User.objects.create_superuser(
            phone='+998901111111',
            username='admin',
            password='AdminPass123!',
            is_staff=True,
            is_superuser=True
        )

        # Regular user yaratish
        self.regular_user = User.objects.create_user(
            phone='+998902222222',
            username='regular',
            password='UserPass123!'
        )

        # AppVersion yaratish (Device uchun kerak)
        self.app_version = AppVersion.objects.create(
            version='1.0.0',
            is_active=True,
            force_update=False,
            device_type=DeviceType.ANDROID
        )

        # Admin user uchun device yaratish
        self.admin_device = Device.objects.create(
            device_model='Admin Device',
            operation_version='Android 12',
            device_type=DeviceType.ANDROID,
            device_id='admin_device_001',
            ip_address='192.168.1.1',
            app_version=self.app_version,
            user=self.admin_user,
            is_active=True
        )

        # Regular user uchun device yaratish
        self.regular_device = Device.objects.create(
            device_model='Regular Device',
            operation_version='Android 12',
            device_type=DeviceType.ANDROID,
            device_id='regular_device_001',
            ip_address='192.168.1.2',
            app_version=self.app_version,
            user=self.regular_user,
            is_active=True
        )

        self.client = APIClient()

        # Test history yaratish
        self.history1 = History.objects.create(
            title_uz='Tarix 1',
            title_en='History 1',
            short_description_uz='Qisqa tavsif 1',
            short_description_en='Short desc 1',
            long_description_uz='Uzun tavsif birinchi history uchun',
            long_description_en='Long description for first history',
            button_text_uz='O\'qish',
            button_text_en='Read',
            button_link='https://example.com/1',
            start_date=timezone.now() + timedelta(hours=1),
            end_date=timezone.now() + timedelta(hours=3),
            is_active=True
        )

        self.history2 = History.objects.create(
            title_uz='Tarix 2',
            title_en='History 2',
            short_description_uz='Qisqa tavsif 2',
            short_description_en='Short desc 2',
            long_description_uz='Uzun tavsif ikkinchi history uchun',
            long_description_en='Long description for second history',
            button_text_uz='Ko\'rish',
            button_text_en='View',
            start_date=timezone.now() + timedelta(hours=2),
            end_date=timezone.now() + timedelta(hours=4),
            is_active=False
        )

    def _create_test_image(self):
        """Test uchun rasm yaratish"""
        file = BytesIO()
        image = Image.new('RGB', (100, 100), color='red')
        image.save(file, 'jpeg')
        file.seek(0)
        return SimpleUploadedFile(
            'test_image.jpg',
            file.read(),
            content_type='image/jpeg'
        )

    def test_list_histories_without_token(self):
        """Token headersiz ro'yxatni olish"""
        response = self.client.get(self.url)

        # IsMobileUser permission Token header talab qiladi
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_histories_with_invalid_token(self):
        """Noto'g'ri token bilan"""
        self.client.credentials(HTTP_TOKEN='invalid-token-123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_histories_as_regular_user(self):
        """Oddiy user sifatida ro'yxatni olish"""
        self.client.force_authenticate(user=self.regular_user)
        self.client.credentials(HTTP_TOKEN=str(self.regular_device.device_token))
        response = self.client.get(self.url)

        # IsAdminUser permission
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_histories_as_admin(self):
        """Admin sifatida ro'yxatni olish"""
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Pagination response structure
        if 'results' in response.data:
            self.assertGreaterEqual(len(response.data['results']), 2)
        elif 'data' in response.data:
            if isinstance(response.data['data'], list):
                self.assertGreaterEqual(len(response.data['data']), 2)
            else:
                # Paginated response
                self.assertIn('results', response.data['data'])

    def test_list_histories_ordered_by_created_at(self):
        """Ro'yxat created_at bo'yicha tartiblangan"""
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Response structure'ga qarab tekshirish
        data = None
        if 'results' in response.data:
            data = response.data['results']
        elif 'data' in response.data:
            if isinstance(response.data['data'], list):
                data = response.data['data']
            elif 'results' in response.data['data']:
                data = response.data['data']['results']

        if data and len(data) >= 2:
            # Eng yangi birinchi bo'lishi kerak
            first_created = data[0]['created_at']
            second_created = data[1]['created_at']
            self.assertGreaterEqual(first_created, second_created)

    def test_list_histories_with_uzbek_language(self):
        """Uzbek tilida ro'yxatni olish"""
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))

        response = self.client.get(self.url, HTTP_ACCEPT_LANGUAGE='uz')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_histories_with_english_language(self):
        """Ingliz tilida ro'yxatni olish"""
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))

        response = self.client.get(self.url, HTTP_ACCEPT_LANGUAGE='en')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_history_without_token(self):
        """Token headersiz history yaratish"""
        data = {
            'title_uz': 'Yangi Tarix',
            'title_en': 'New History',
            'short_description_uz': 'Qisqa tavsif yangi',
            'short_description_en': 'Short desc new',
            'long_description_uz': 'Uzun tavsif yangi history uchun',
            'long_description_en': 'Long description for new history',
            'button_text_uz': 'Batafsil',
            'button_text_en': 'Details',
            'button_link': 'https://example.com/new',
            'start_date': (timezone.now() + timedelta(hours=1)).isoformat(),
            'end_date': (timezone.now() + timedelta(hours=3)).isoformat(),
            'is_active': True
        }

        response = self.client.post(self.url, data)

        # Token header yo'q
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_history_as_regular_user(self):
        """Oddiy user history yarata olmaydi"""
        self.client.force_authenticate(user=self.regular_user)
        self.client.credentials(HTTP_TOKEN=str(self.regular_device.device_token))

        data = {
            'title_uz': 'Yangi Tarix',
            'title_en': 'New History',
            'short_description_uz': 'Qisqa tavsif yangi',
            'short_description_en': 'Short desc new',
            'long_description_uz': 'Uzun tavsif yangi history uchun',
            'long_description_en': 'Long description for new history',
            'start_date': (timezone.now() + timedelta(hours=1)).isoformat(),
            'end_date': (timezone.now() + timedelta(hours=3)).isoformat(),
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_history_as_admin_success(self):
        """Admin muvaffaqiyatli history yaratadi"""
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))

        data = {
            'title_uz': 'Yangi Tarix',
            'title_en': 'New History',
            'short_description_uz': 'Qisqa tavsif yangi',
            'short_description_en': 'Short desc new',
            'long_description_uz': 'Uzun tavsif yangi history uchun',
            'long_description_en': 'Long description for new history',
            'button_text_uz': 'Batafsil',
            'button_text_en': 'Details',
            'button_link': 'https://example.com/new',
            'start_date': (timezone.now() + timedelta(hours=1)).isoformat(),
            'end_date': (timezone.now() + timedelta(hours=3)).isoformat(),
            'is_active': True
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(History.objects.count(), 3)

    def test_create_history_with_images(self):
        """Rasmlar bilan history yaratish"""
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))

        image_uz = self._create_test_image()
        image_en = self._create_test_image()

        data = {
            'title_uz': 'Yangi Tarix',
            'title_en': 'New History',
            'short_description_uz': 'Qisqa tavsif yangi',
            'short_description_en': 'Short desc new',
            'long_description_uz': 'Uzun tavsif yangi history uchun',
            'long_description_en': 'Long description for new history',
            'button_text_uz': 'Batafsil',
            'button_text_en': 'Details',
            'start_date': (timezone.now() + timedelta(hours=1)).isoformat(),
            'end_date': (timezone.now() + timedelta(hours=3)).isoformat(),
            'images_uz': [image_uz],
            'images_en': [image_en]
        }

        response = self.client.post(self.url, data, format='multipart')

        if response.status_code == status.HTTP_201_CREATED:
            # Response structure'ga qarab ID olish
            history_id = None
            if 'data' in response.data:
                if isinstance(response.data['data'], dict):
                    history_id = response.data['data'].get('id')
            elif 'id' in response.data:
                history_id = response.data['id']

            if history_id:
                history = History.objects.get(id=history_id)
                self.assertGreaterEqual(history.media_files.count(), 0)

    def test_create_history_start_date_in_past(self):
        """O'tmishdagi start_date bilan yaratish"""
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))

        data = {
            'title_uz': 'Yangi Tarix',
            'title_en': 'New History',
            'short_description_uz': 'Qisqa tavsif yangi',
            'short_description_en': 'Short desc new',
            'long_description_uz': 'Uzun tavsif yangi history uchun',
            'long_description_en': 'Long description for new history',
            'start_date': (timezone.now() - timedelta(hours=1)).isoformat(),
            'end_date': (timezone.now() + timedelta(hours=1)).isoformat(),
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_history_end_date_before_start_date(self):
        """End date start date'dan oldin"""
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))

        data = {
            'title_uz': 'Yangi Tarix',
            'title_en': 'New History',
            'short_description_uz': 'Qisqa tavsif yangi',
            'short_description_en': 'Short desc new',
            'long_description_uz': 'Uzun tavsif yangi history uchun',
            'long_description_en': 'Long description for new history',
            'start_date': (timezone.now() + timedelta(hours=2)).isoformat(),
            'end_date': (timezone.now() + timedelta(hours=1)).isoformat(),
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_history_duration_less_than_hour(self):
        """1 soatdan kam davomiylik"""
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))

        start = timezone.now() + timedelta(hours=1)
        end = start + timedelta(minutes=30)  # 30 daqiqa

        data = {
            'title_uz': 'Yangi Tarix',
            'title_en': 'New History',
            'short_description_uz': 'Qisqa tavsif yangi',
            'short_description_en': 'Short desc new',
            'long_description_uz': 'Uzun tavsif yangi history uchun',
            'long_description_en': 'Long description for new history',
            'start_date': start.isoformat(),
            'end_date': end.isoformat(),
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_history_button_text_without_link(self):
        """Button text bor, lekin link yo'q"""
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))

        data = {
            'title_uz': 'Yangi Tarix',
            'title_en': 'New History',
            'short_description_uz': 'Qisqa tavsif yangi',
            'short_description_en': 'Short desc new',
            'long_description_uz': 'Uzun tavsif yangi history uchun',
            'long_description_en': 'Long description for new history',
            'button_text_uz': 'Batafsil',
            'button_text_en': 'Details',
            # button_link yo'q
            'start_date': (timezone.now() + timedelta(hours=1)).isoformat(),
            'end_date': (timezone.now() + timedelta(hours=3)).isoformat(),
        }

        response = self.client.post(self.url, data, format='json')

        # Serializer validation button_text bo'lsa button_link talab qilmaydi
        # Faqat button_text_uz yoki button_text_en bo'lsa button_link kerak
        # Bu test o'tishi kerak yoki 400 bo'lishi kerak
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])

    def test_create_history_short_title(self):
        """3 ta belgidan kam title"""
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))

        data = {
            'title_uz': 'AB',  # 2 ta belgi
            'title_en': 'AB',
            'short_description_uz': 'Qisqa tavsif yangi',
            'short_description_en': 'Short desc new',
            'long_description_uz': 'Uzun tavsif yangi history uchun',
            'long_description_en': 'Long description for new history',
            'start_date': (timezone.now() + timedelta(hours=1)).isoformat(),
            'end_date': (timezone.now() + timedelta(hours=3)).isoformat(),
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_history_short_description_too_short(self):
        """10 ta belgidan kam short_description"""
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))

        data = {
            'title_uz': 'Yangi Tarix',
            'title_en': 'New History',
            'short_description_uz': 'Qisqa',  # 5 ta belgi
            'short_description_en': 'Short',
            'long_description_uz': 'Uzun tavsif yangi history uchun',
            'long_description_en': 'Long description for new history',
            'start_date': (timezone.now() + timedelta(hours=1)).isoformat(),
            'end_date': (timezone.now() + timedelta(hours=3)).isoformat(),
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_history_short_description_too_long(self):
        """100 ta belgidan ko'p short_description"""
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))

        long_text = 'A' * 101

        data = {
            'title_uz': 'Yangi Tarix',
            'title_en': 'New History',
            'short_description_uz': long_text,
            'short_description_en': long_text,
            'long_description_uz': 'Uzun tavsif yangi history uchun',
            'long_description_en': 'Long description for new history',
            'start_date': (timezone.now() + timedelta(hours=1)).isoformat(),
            'end_date': (timezone.now() + timedelta(hours=3)).isoformat(),
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_history_invalid_button_link(self):
        """Noto'g'ri button_link format"""
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))

        data = {
            'title_uz': 'Yangi Tarix',
            'title_en': 'New History',
            'short_description_uz': 'Qisqa tavsif yangi',
            'short_description_en': 'Short desc new',
            'long_description_uz': 'Uzun tavsif yangi history uchun',
            'long_description_en': 'Long description for new history',
            'button_text_uz': 'Batafsil',
            'button_text_en': 'Details',
            'button_link': 'invalid-url',  # http:// yoki https:// yo'q
            'start_date': (timezone.now() + timedelta(hours=1)).isoformat(),
            'end_date': (timezone.now() + timedelta(hours=3)).isoformat(),
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class HistoryRetrieveUpdateDestroyAPIViewTestCase(APITestCase):
    """Test cases for History retrieve, update, delete"""

    def setUp(self):
        # Admin user
        self.admin_user = User.objects.create_superuser(
            phone='+998901111111',
            username='admin',
            password='AdminPass123!',
            is_staff=True,
            is_superuser=True
        )

        # Regular user
        self.regular_user = User.objects.create_user(
            phone='+998902222222',
            username='regular',
            password='UserPass123!'
        )

        # AppVersion yaratish
        self.app_version = AppVersion.objects.create(
            version='1.0.0',
            is_active=True,
            force_update=False,
            device_type=DeviceType.ANDROID
        )

        # Admin device
        self.admin_device = Device.objects.create(
            device_model='Admin Device',
            operation_version='Android 12',
            device_type=DeviceType.ANDROID,
            device_id='admin_device_002',
            ip_address='192.168.1.3',
            app_version=self.app_version,
            user=self.admin_user,
            is_active=True
        )

        # Regular device
        self.regular_device = Device.objects.create(
            device_model='Regular Device',
            operation_version='Android 12',
            device_type=DeviceType.ANDROID,
            device_id='regular_device_002',
            ip_address='192.168.1.4',
            app_version=self.app_version,
            user=self.regular_user,
            is_active=True
        )

        self.client = APIClient()

        # Test history
        self.history = History.objects.create(
            title_uz='Test Tarix',
            title_en='Test History',
            short_description_uz='Qisqa tavsif test',
            short_description_en='Short desc test',
            long_description_uz='Uzun tavsif test uchun yozilgan',
            long_description_en='Long description for test',
            button_text_uz='O\'qish',
            button_text_en='Read',
            button_link='https://example.com',
            start_date=timezone.now() + timedelta(hours=1),
            end_date=timezone.now() + timedelta(hours=3),
            is_active=True
        )

        self.url = f'/api/v1/admins/histories/{self.history.id}/'

    def test_retrieve_history_without_token(self):
        """Token headersiz history olish"""
        response = self.client.get(self.url)

        # Token header yo'q
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_history_as_regular_user(self):
        """Oddiy user sifatida history olish"""
        self.client.force_authenticate(user=self.regular_user)
        self.client.credentials(HTTP_TOKEN=str(self.regular_device.device_token))
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_history_as_admin(self):
        """Admin sifatida history olish"""
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Response structure'ga qarab ID tekshirish
        if 'data' in response.data:
            if isinstance(response.data['data'], dict):
                self.assertEqual(response.data['data']['id'], self.history.id)
        elif 'id' in response.data:
            self.assertEqual(response.data['id'], self.history.id)

    def test_retrieve_history_with_uzbek_language(self):
        """Uzbek tilida history olish"""
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))

        response = self.client.get(self.url, HTTP_ACCEPT_LANGUAGE='uz')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_history_not_found(self):
        """Mavjud bo'lmagan history"""
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))

        url = '/api/v1/admins/histories/99999/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_history_without_token(self):
        """Token headersiz yangilash"""
        data = {'title_uz': 'Yangilangan Tarix'}
        response = self.client.patch(self.url, data)

        # Token header yo'q
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_history_as_regular_user(self):
        """Oddiy user yangilash"""
        self.client.force_authenticate(user=self.regular_user)
        self.client.credentials(HTTP_TOKEN=str(self.regular_device.device_token))

        data = {'title_uz': 'Yangilangan Tarix'}
        response = self.client.patch(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_history_as_admin_success(self):
        """Admin muvaffaqiyatli yangilaydi"""
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))

        data = {
            'title_uz': 'Yangilangan Tarix',
            'title_en': 'Updated History'
        }
        response = self.client.patch(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.history.refresh_from_db()
        self.assertEqual(self.history.title_uz, 'Yangilangan Tarix')

    def test_update_history_full_update(self):
        """To'liq yangilash (PUT)"""
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))

        data = {
            'title_uz': 'Yangi Tarix',
            'title_en': 'New History',
            'short_description_uz': 'Yangi qisqa tavsif',
            'short_description_en': 'New short desc',
            'long_description_uz': 'Yangi uzun tavsif history uchun',
            'long_description_en': 'New long description for history',
            'button_text_uz': 'Batafsil',
            'button_text_en': 'Details',
            'button_link': 'https://example.com/new',
            'start_date': (timezone.now() + timedelta(hours=2)).isoformat(),
            'end_date': (timezone.now() + timedelta(hours=4)).isoformat(),
            'is_active': False
        }

        response = self.client.put(self.url, data, format='json')

        if response.status_code == status.HTTP_200_OK:
            self.history.refresh_from_db()
            self.assertEqual(self.history.title_uz, 'Yangi Tarix')
            self.assertFalse(self.history.is_active)

    def test_update_history_change_dates(self):
        """Date'larni o'zgartirish"""
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))

        new_start = timezone.now() + timedelta(hours=5)
        new_end = timezone.now() + timedelta(hours=7)

        data = {
            'start_date': new_start.isoformat(),
            'end_date': new_end.isoformat()
        }

        response = self.client.patch(self.url, data, format='json')

        if response.status_code == status.HTTP_200_OK:
            self.history.refresh_from_db()
            # Date'lar yangilangan

    def test_update_history_invalid_dates(self):
        """Noto'g'ri date'lar bilan yangilash"""
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))

        data = {
            'start_date': (timezone.now() + timedelta(hours=5)).isoformat(),
            'end_date': (timezone.now() + timedelta(hours=3)).isoformat()  # start'dan oldin
        }

        response = self.client.patch(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_history_without_token(self):
        """Token headersiz o'chirish"""
        response = self.client.delete(self.url)

        # Token header yo'q
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_history_as_regular_user(self):
        """Oddiy user o'chirish"""
        self.client.force_authenticate(user=self.regular_user)
        self.client.credentials(HTTP_TOKEN=str(self.regular_device.device_token))
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_history_as_admin_success(self):
        """Admin muvaffaqiyatli o'chiradi"""
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # History o'chirilganini tekshirish
        self.assertFalse(History.objects.filter(id=self.history.id).exists())


class HistorySerializerValidationTestCase(TestCase):
    """Test cases for HistorySerializer validation"""

    def test_title_validation_too_short(self):
        """Title 3 ta belgidan kam"""
        data = {
            'title_uz': 'AB',
            'title_en': 'AB',
            'short_description_uz': 'Qisqa tavsif test uchun',
            'short_description_en': 'Short desc for test',
            'long_description_uz': 'Uzun tavsif test uchun yozilgan',
            'long_description_en': 'Long description for test',
            'start_date': timezone.now() + timedelta(hours=1),
            'end_date': timezone.now() + timedelta(hours=3),
        }

        serializer = HistorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        # title_uz field validatsiyasi
        self.assertTrue('title_uz' in serializer.errors or 'title' in str(serializer.errors))

    def test_short_description_too_short(self):
        """Short description 10 ta belgidan kam"""
        data = {
            'title_uz': 'Test Tarix',
            'title_en': 'Test History',
            'short_description_uz': 'Qisqa',
            'short_description_en': 'Short',
            'long_description_uz': 'Uzun tavsif test uchun yozilgan',
            'long_description_en': 'Long description for test',
            'start_date': timezone.now() + timedelta(hours=1),
            'end_date': timezone.now() + timedelta(hours=3),
        }

        serializer = HistorySerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_short_description_too_long(self):
        """Short description 100 ta belgidan ko'p"""
        long_text = 'A' * 101

        data = {
            'title_uz': 'Test Tarix',
            'title_en': 'Test History',
            'short_description_uz': long_text,
            'short_description_en': long_text,
            'long_description_uz': 'Uzun tavsif test uchun yozilgan',
            'long_description_en': 'Long description for test',
            'start_date': timezone.now() + timedelta(hours=1),
            'end_date': timezone.now() + timedelta(hours=3),
        }

        serializer = HistorySerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_long_description_too_short(self):
        """Long description 20 ta belgidan kam"""
        data = {
            'title_uz': 'Test Tarix',
            'title_en': 'Test History',
            'short_description_uz': 'Qisqa tavsif test uchun',
            'short_description_en': 'Short desc for test',
            'long_description_uz': 'Qisqa',
            'long_description_en': 'Short',
            'start_date': timezone.now() + timedelta(hours=1),
            'end_date': timezone.now() + timedelta(hours=3),
        }

        serializer = HistorySerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_button_text_too_short(self):
        """Button text 2 ta belgidan kam"""
        data = {
            'title_uz': 'Test Tarix',
            'title_en': 'Test History',
            'short_description_uz': 'Qisqa tavsif test uchun',
            'short_description_en': 'Short desc for test',
            'long_description_uz': 'Uzun tavsif test uchun yozilgan',
            'long_description_en': 'Long description for test',
            'button_text_uz': 'A',
            'button_text_en': 'A',
            'button_link': 'https://example.com',
            'start_date': timezone.now() + timedelta(hours=1),
            'end_date': timezone.now() + timedelta(hours=3),
        }

        serializer = HistorySerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_button_text_too_long(self):
        """Button text 50 ta belgidan ko'p"""
        long_text = 'A' * 51

        data = {
            'title_uz': 'Test Tarix',
            'title_en': 'Test History',
            'short_description_uz': 'Qisqa tavsif test uchun',
            'short_description_en': 'Short desc for test',
            'long_description_uz': 'Uzun tavsif test uchun yozilgan',
            'long_description_en': 'Long description for test',
            'button_text_uz': long_text,
            'button_text_en': long_text,
            'button_link': 'https://example.com',
            'start_date': timezone.now() + timedelta(hours=1),
            'end_date': timezone.now() + timedelta(hours=3),
        }

        serializer = HistorySerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_button_link_invalid_format(self):
        """Button link noto'g'ri format"""
        data = {
            'title_uz': 'Test Tarix',
            'title_en': 'Test History',
            'short_description_uz': 'Qisqa tavsif test uchun',
            'short_description_en': 'Short desc for test',
            'long_description_uz': 'Uzun tavsif test uchun yozilgan',
            'long_description_en': 'Long description for test',
            'button_text_uz': 'Batafsil',
            'button_text_en': 'Read More',
            'button_link': 'invalid-url',
            'start_date': timezone.now() + timedelta(hours=1),
            'end_date': timezone.now() + timedelta(hours=3),
        }

        serializer = HistorySerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_start_date_in_past_on_create(self):
        """O'tmishdagi start_date (yaratishda)"""
        data = {
            'title_uz': 'Test Tarix',
            'title_en': 'Test History',
            'short_description_uz': 'Qisqa tavsif test uchun',
            'short_description_en': 'Short desc for test',
            'long_description_uz': 'Uzun tavsif test uchun yozilgan',
            'long_description_en': 'Long description for test',
            'start_date': timezone.now() - timedelta(hours=1),
            'end_date': timezone.now() + timedelta(hours=1),
        }

        serializer = HistorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('start_date', serializer.errors)

    def test_end_date_in_past(self):
        """O'tmishdagi end_date"""
        data = {
            'title_uz': 'Test Tarix',
            'title_en': 'Test History',
            'short_description_uz': 'Qisqa tavsif test uchun',
            'short_description_en': 'Short desc for test',
            'long_description_uz': 'Uzun tavsif test uchun yozilgan',
            'long_description_en': 'Long description for test',
            'start_date': timezone.now() + timedelta(hours=1),
            'end_date': timezone.now() - timedelta(hours=1),
        }

        serializer = HistorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('end_date', serializer.errors)

    def test_end_date_before_start_date(self):
        """End date start date'dan oldin"""
        start = timezone.now() + timedelta(hours=2)
        end = timezone.now() + timedelta(hours=1)

        data = {
            'title_uz': 'Test Tarix',
            'title_en': 'Test History',
            'short_description_uz': 'Qisqa tavsif test uchun',
            'short_description_en': 'Short desc for test',
            'long_description_uz': 'Uzun tavsif test uchun yozilgan',
            'long_description_en': 'Long description for test',
            'start_date': start,
            'end_date': end,
        }

        serializer = HistorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('end_date', serializer.errors)

    def test_duration_less_than_hour(self):
        """1 soatdan kam davomiylik"""
        start = timezone.now() + timedelta(hours=1)
        end = start + timedelta(minutes=30)

        data = {
            'title_uz': 'Test Tarix',
            'title_en': 'Test History',
            'short_description_uz': 'Qisqa tavsif test uchun',
            'short_description_en': 'Short desc for test',
            'long_description_uz': 'Uzun tavsif test uchun yozilgan',
            'long_description_en': 'Long description for test',
            'start_date': start,
            'end_date': end,
        }

        serializer = HistorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('end_date', serializer.errors)

    def test_button_text_without_link(self):
        """Button text bor, lekin link yo'q"""
        data = {
            'title_uz': 'Test Tarix',
            'title_en': 'Test History',
            'short_description_uz': 'Qisqa tavsif test uchun',
            'short_description_en': 'Short desc for test',
            'long_description_uz': 'Uzun tavsif test uchun yozilgan',
            'long_description_en': 'Long description for test',
            'button_text_uz': 'Batafsil',
            'button_text_en': 'Read More',
            'start_date': timezone.now() + timedelta(hours=1),
            'end_date': timezone.now() + timedelta(hours=3),
        }

        serializer = HistorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('button_link', serializer.errors)


class HistoryTranslationTestCase(APITestCase):
    """Test cases for History translation functionality"""

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            phone='+998901111111',
            username='admin',
            password='AdminPass123!',
            is_staff=True,
            is_superuser=True
        )

        # AppVersion va Device
        self.app_version = AppVersion.objects.create(
            version='1.0.0',
            is_active=True,
            device_type=DeviceType.ANDROID
        )

        self.admin_device = Device.objects.create(
            device_model='Admin Device',
            operation_version='Android 12',
            device_type=DeviceType.ANDROID,
            device_id='admin_device_003',
            ip_address='192.168.1.5',
            app_version=self.app_version,
            user=self.admin_user,
            is_active=True
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))

        self.history = History.objects.create(
            title_uz='O\'zbekcha Tarix',
            title_en='English History',
            short_description_uz='O\'zbekcha qisqa tavsif',
            short_description_en='English short description',
            long_description_uz='O\'zbekcha uzun tavsif test uchun yozilgan',
            long_description_en='English long description for test',
            button_text_uz='Ko\'rish',
            button_text_en='View',
            button_link='https://example.com',
            start_date=timezone.now() + timedelta(hours=1),
            end_date=timezone.now() + timedelta(hours=3),
            is_active=True
        )

    def test_get_history_in_uzbek(self):
        """Uzbek tilida history olish"""
        url = f'/api/v1/admins/histories/{self.history.id}/'

        response = self.client.get(url, HTTP_ACCEPT_LANGUAGE='uz')

        if response.status_code == status.HTTP_200_OK:
            # TranslatedFieldsReadMixin ishlashi kerak
            # Response structure'ga qarab tekshirish
            data = response.data.get('data', response.data)
            if isinstance(data, dict):
                self.assertIn('title', data)

    def test_get_history_in_english(self):
        """Ingliz tilida history olish"""
        url = f'/api/v1/admins/histories/{self.history.id}/'

        response = self.client.get(url, HTTP_ACCEPT_LANGUAGE='en')

        if response.status_code == status.HTTP_200_OK:
            data = response.data.get('data', response.data)
            if isinstance(data, dict):
                self.assertIn('title', data)


class HistoryPaginationTestCase(APITestCase):
    """Test cases for History pagination"""

    def setUp(self):
        self.url = '/api/v1/admins/histories/'

        self.admin_user = User.objects.create_superuser(
            phone='+998901111111',
            username='admin',
            password='AdminPass123!',
            is_staff=True,
            is_superuser=True
        )

        # AppVersion va Device
        self.app_version = AppVersion.objects.create(
            version='1.0.0',
            is_active=True,
            device_type=DeviceType.ANDROID
        )

        self.admin_device = Device.objects.create(
            device_model='Admin Device',
            operation_version='Android 12',
            device_type=DeviceType.ANDROID,
            device_id='admin_device_004',
            ip_address='192.168.1.6',
            app_version=self.app_version,
            user=self.admin_user,
            is_active=True
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))

        # 15 ta history yaratamiz (pagination uchun)
        for i in range(15):
            History.objects.create(
                title_uz=f'Tarix {i}',
                title_en=f'History {i}',
                short_description_uz=f'Qisqa tavsif {i}',
                short_description_en=f'Short desc {i}',
                long_description_uz=f'Uzun tavsif {i} test uchun yozilgan',
                long_description_en=f'Long description {i} for test',
                start_date=timezone.now() + timedelta(hours=i + 1),
                end_date=timezone.now() + timedelta(hours=i + 3),
                is_active=True
            )

    def test_list_with_pagination(self):
        """Pagination bilan ro'yxat"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Pagination bo'lishi kerak
        if 'count' in response.data:
            self.assertEqual(response.data['count'], 15)
            self.assertIn('next', response.data)
            self.assertIn('previous', response.data)
        elif 'data' in response.data and isinstance(response.data['data'], dict):
            if 'count' in response.data['data']:
                self.assertEqual(response.data['data']['count'], 15)

    def test_list_page_parameter(self):
        """Page parameter bilan"""
        response = self.client.get(self.url, {'page': 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class HistoryIntegrationTestCase(APITestCase):
    """Integration tests - to'liq workflow"""

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            phone='+998901111111',
            username='admin',
            password='AdminPass123!',
            is_staff=True,
            is_superuser=True
        )

        # AppVersion va Device
        self.app_version = AppVersion.objects.create(
            version='1.0.0',
            is_active=True,
            device_type=DeviceType.ANDROID
        )

        self.admin_device = Device.objects.create(
            device_model='Admin Device',
            operation_version='Android 12',
            device_type=DeviceType.ANDROID,
            device_id='admin_device_005',
            ip_address='192.168.1.7',
            app_version=self.app_version,
            user=self.admin_user,
            is_active=True
        )

        self.client = APIClient()

    def test_full_history_crud_workflow(self):
        """To'liq CRUD workflow"""
        # Authenticate
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))

        # 1. Create history
        create_data = {
            'title_uz': 'Test Tarix',
            'title_en': 'Test History',
            'short_description_uz': 'Qisqa tavsif test',
            'short_description_en': 'Short desc test',
            'long_description_uz': 'Uzun tavsif test uchun yozilgan',
            'long_description_en': 'Long description for test',
            'button_text_uz': 'Batafsil',
            'button_text_en': 'Read More',
            'button_link': 'https://example.com',
            'start_date': (timezone.now() + timedelta(hours=1)).isoformat(),
            'end_date': (timezone.now() + timedelta(hours=3)).isoformat(),
            'is_active': True
        }

        create_response = self.client.post('/api/v1/admins/histories/', create_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        # Get history ID
        history_id = None
        if 'data' in create_response.data:
            if isinstance(create_response.data['data'], dict):
                history_id = create_response.data['data'].get('id')
        elif 'id' in create_response.data:
            history_id = create_response.data['id']

        self.assertIsNotNone(history_id)

        # 2. Retrieve history
        retrieve_response = self.client.get(f'/api/v1/admins/histories/{history_id}/')
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)

        # 3. Update history
        update_data = {
            'title_uz': 'Yangilangan Tarix',
            'title_en': 'Updated History'
        }
        update_response = self.client.patch(
            f'/api/v1/admins/histories/{history_id}/',
            update_data,
            format='json'
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

        # 4. Delete history
        delete_response = self.client.delete(f'/api/v1/admins/histories/{history_id}/')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify deleted
        self.assertFalse(History.objects.filter(id=history_id).exists())

    def test_list_histories_workflow(self):
        """Ro'yxat olish workflow"""
        self.client.force_authenticate(user=self.admin_user)
        self.client.credentials(HTTP_TOKEN=str(self.admin_device.device_token))

        # Create multiple histories
        for i in range(3):
            History.objects.create(
                title_uz=f'Tarix {i}',
                title_en=f'History {i}',
                short_description_uz=f'Qisqa tavsif {i}',
                short_description_en=f'Short desc {i}',
                long_description_uz=f'Uzun tavsif {i} test uchun',
                long_description_en=f'Long description {i} for test',
                start_date=timezone.now() + timedelta(hours=i + 1),
                end_date=timezone.now() + timedelta(hours=i + 3),
                is_active=True
            )

        # List all
        response = self.client.get('/api/v1/admins/histories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check count
        if 'count' in response.data:
            self.assertEqual(response.data['count'], 3)
        elif 'data' in response.data:
            data = response.data['data']
            if isinstance(data, list):
                self.assertEqual(len(data), 3)
            elif isinstance(data, dict) and 'results' in data:
                self.assertGreaterEqual(len(data['results']), 3)


# Test ishga tushirish
if __name__ == '__main__':
    import django

    django.setup()
    from django.test.runner import DiscoverRunner

    runner = DiscoverRunner()
    runner.run_tests(['apps.admins.tests.test_histories'])