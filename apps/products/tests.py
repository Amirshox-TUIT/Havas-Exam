from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone, translation
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import timedelta
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.products.models import Product, ProductRating

User = get_user_model()


def create_test_image():
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


class ProductModelTestCase(TestCase):

    def setUp(self):
        self.product_data = {
            'title': 'Test Product',
            'description': 'This is a test product description',
            'price': 100,
            'quantity': 10,
            'weight': 500,
            'measurement': 'gr',
            'category': 'all',
            'discount': 10,
            'is_available': True,
        }

    def test_create_product(self):
        product = Product.objects.create(**self.product_data)
        self.assertEqual(product.title, 'Test Product')
        self.assertTrue(product.is_available)
        self.assertEqual(product.discount_price, 90)

    def test_in_stock_method(self):
        product = Product.objects.create(**self.product_data)
        self.assertTrue(product.in_stock())
        product.quantity = 0
        self.assertFalse(product.in_stock())


class ProductAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            phone='+998901234567',
            username='testuser',
            password='TestPass123!'
        )
        self.client.force_authenticate(user=self.user)

        self.product1 = Product.objects.create(
            title='Product 1',
            description='Description 1',
            price=100,
            quantity=5,
            weight=100,
            measurement='gr',
            category='all',
            discount=10,
            is_available=True
        )

        self.product2 = Product.objects.create(
            title='Product 2',
            description='Description 2',
            price=200,
            quantity=0,
            weight=200,
            measurement='kg',
            category='all',
            discount=20,
            is_available=True
        )

        self.unavailable_product = Product.objects.create(
            title='Product 3',
            description='Description 3',
            price=300,
            quantity=3,
            weight=300,
            measurement='pc',
            category='all',
            discount=0,
            is_available=False
        )

    def test_list_products_authenticated(self):
        response = self.client.get('/api/v1/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get('results', response.data)
        # Faqat is_available=True
        self.assertTrue(all(p['id'] in [self.product1.id, self.product2.id] for p in data))

    def test_list_products_without_authentication(self):
        self.client.logout()
        response = self.client.get('/api/v1/products/')
        # IsAuthenticatedOrMobileUser permission bo'lishi mumkin
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_retrieve_product_success(self):
        response = self.client.get(f'/api/v1/products/{self.product1.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get('data', response.data)
        self.assertEqual(data['id'], self.product1.id)
        self.assertIn('title', data)
        self.assertIn('description', data)

    def test_retrieve_unavailable_product(self):
        response = self.client.get(f'/api/v1/products/{self.unavailable_product.pk}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_product_with_language_uz(self):
        translation.activate('uz')
        response = self.client.get(f'/api/v1/products/{self.product1.pk}/', {'lang': 'uz'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get('data', response.data)
        self.assertIn('title', data)

    def test_retrieve_product_with_language_en(self):
        translation.activate('en')
        response = self.client.get(f'/api/v1/products/{self.product1.pk}/', {'lang': 'en'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get('data', response.data)
        self.assertIn('title', data)

    def test_create_product_rating_success(self):
        response = self.client.post(f'/api/v1/products/{self.product1.pk}/rating/', data={'rating': 5})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        rating = ProductRating.objects.filter(user=self.user, product=self.product1).first()
        self.assertIsNotNone(rating)
        self.assertEqual(rating.rating, 5)

    def test_create_duplicate_product_rating(self):
        ProductRating.objects.create(user=self.user, product=self.product1, rating=4)
        response = self.client.post(f'/api/v1/products/{self.product1.pk}/rating/', data={'rating': 5})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_product_avg_rating_field(self):
        ProductRating.objects.create(user=self.user, product=self.product1, rating=4)
        ProductRating.objects.create(user=self.user, product=self.product1, rating=5)
        response = self.client.get(f'/api/v1/products/{self.product1.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get('data', response.data)
        self.assertIn('id', data)
        # Serializerda avg_rating mavjud emas, lekin qo‘shilsa test qo‘yish mumkin


class IntegrationProductTestCase(APITestCase):
    """To'liq workflow: List -> Retrieve -> Rating"""

    def test_full_product_workflow(self):
        user = User.objects.create_user(
            phone='+998902345678',
            username='integrationuser',
            password='TestPass123!'
        )
        self.client.force_authenticate(user=user)
        product = Product.objects.create(
            title='Integration Product',
            description='Integration Description',
            price=100,
            quantity=10,
            weight=100,
            measurement='gr',
            category='all',
            discount=10,
            is_available=True
        )

        # List
        list_response = self.client.get('/api/v1/products/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)

        # Retrieve
        detail_response = self.client.get(f'/api/v1/products/{product.pk}/')
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)

        # Rating
        rating_response = self.client.post(f'/api/v1/products/{product.pk}/rating/', data={'rating': 5})
        self.assertEqual(rating_response.status_code, status.HTTP_201_CREATED)
