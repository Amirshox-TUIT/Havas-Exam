import json
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from apps.products.models import Product, ProductRating, ProductCategory, Measurement
from apps.users.models.device import Device, AppVersion, DeviceType

User = get_user_model()


class ProductTestCase(APITestCase):
    """Base test case with common setup for product tests"""

    def setUp(self):
        self.client = APIClient()

        self.admin_user = User.objects.create_superuser(
            username="admin",
            phone="+998901111111",
            password="admin123",
            is_active=True
        )

        self.user = User.objects.create_user(
            username="testuser",
            phone="+998901234567",
            password="testpass123",
            is_active=True
        )

        self.user2 = User.objects.create_user(
            username="testuser2",
            phone="+998907654321",
            password="testpass123",
            is_active=True
        )

        self.app_version = AppVersion.objects.create(version="1.0.0", is_active=True,
                                                     device_type=DeviceType.ANDROID)
        self.device = Device.objects.create( device_model="Test Device", operation_version="Android 12", device_type=DeviceType.ANDROID, device_id="test_device_123", ip_address="127.0.0.1", app_version=self.app_version )

        self.product1 = Product.objects.create( title_en="Test Product 1", title_uz="Test Mahsulot 1", description_en="This is a test product description with more than 30 characters", description_uz="Bu test mahsulot tavsifi 30 belgidan ortiq bo'lishi kerak", price=Decimal("100.00"), quantity=10, weight=500, measurement=Measurement.GR, category=ProductCategory.BF, discount=10, is_available=True )
        self.product2 = Product.objects.create( title_en="Test Product 2", title_uz="Test Mahsulot 2", description_en="Another test product with detailed description text", description_uz="Boshqa test mahsulot batafsil tavsif matni bilan", price=Decimal("200.00"), quantity=5, weight=1000, measurement=Measurement.KG, category=ProductCategory.LU, discount=20, is_available=True )
        self.unavailable_product = Product.objects.create( title_en="Unavailable Product", title_uz="Mavjud bo'lmagan mahsulot", description_en="This product should not appear in lists", description_uz="Bu mahsulot ro'yxatda ko'rinmasligi kerak", price=Decimal("150.00"), quantity=0, is_available=False )
        self.rating = ProductRating.objects.create( user=self.user, product=self.product2, rating=5 )
        self.list_url = '/api/v1/products/'
        self.detail_url = lambda pk: f'/api/v1/products/{pk}/'
        self.rating_url = lambda pk: f'/api/v1/products/{pk}/rating/'

        # URL lar
        self.list_url = '/api/v1/products/'
        self.detail_url = lambda pk: f'/api/v1/products/{pk}/'
        self.rating_url = lambda pk: f'/api/v1/products/{pk}/rating/'

    def login(self, user):
        """login user via JWT and attach Bearer header"""
        resp = self.client.post("/api/v1/users/login/", {
            "phone": user.phone,
            "password": "testpass123" if user != self.admin_user else "admin123"
        }, format="json")

        assert resp.status_code == 200, f"Login error: {resp.data}"

        access = resp.data["data"]["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")


class ProductListAPIViewTest(ProductTestCase):
    """Tests for ProductListAPIView"""
    def test_list_products_with_admin_user(self):
        """Test listing products with admin user"""
        self.client.login(user=self.admin_user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)

    def test_list_products_without_authentication(self):
        """Test listing products without any authentication"""
        response = self.client.get(self.list_url)

        # Should fail without authentication
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_list_products_filters_unavailable(self):
        """Test that unavailable products are not listed"""
        self.login(self.user2)
        response = self.client.get(self.list_url)

        results = response.data['data']['results']
        product_ids = [p['id'] for p in results]
        self.assertNotIn(self.unavailable_product.id, product_ids)

    def test_list_products_response_structure(self):
        """Test the structure of product list response"""
        self.login(self.user2)
        response = self.client.get(self.list_url)

        results = response.data['data']['results']
        product = results[0]
        expected_fields = [
            'id', 'title', 'price', 'discount_price',
            'quantity', 'weight', 'measurement',
            'category', 'discount'
        ]

        for field in expected_fields:
            self.assertIn(field, product)

    def test_list_products_returns_translated_title(self):
        """Test that products return translated title based on language"""
        self.login(self.user2)
        response = self.client.get(self.list_url)

        results = response.data['data']['results']
        product = results[0]
        # Default language is 'en' in TranslatedFieldsReadMixin
        self.assertIn('title', product)
        self.assertNotIn('title_en', product)
        self.assertNotIn('title_uz', product)

    def test_list_products_discount_price_calculation(self):
        """Test that discount price is calculated correctly"""
        self.login(self.user2)
        response = self.client.get(self.list_url)

        results = response.data['data']['results']
        # Find product1 in results
        product = next(p for p in results if p['id'] == self.product1.id)

        # Product1: price=100, discount=10% => discount_price=90
        expected_price = Decimal("90.00")
        actual_price = Decimal(str(product['discount_price']))
        self.assertEqual(actual_price, expected_price)

    def test_list_products_pagination(self):
        """Test product list pagination"""
        self.login(self.user2)
        response = self.client.get(self.list_url)

        # Check pagination structure
        self.assertIn('data', response.data)
        data = response.data['data']
        self.assertIn('count', data)
        self.assertIn('results', data)


class ProductRetrieveAPIViewTest(ProductTestCase):
    """Tests for ProductRetrieveAPIView"""

    def test_retrieve_product_with_admin_user(self):
        """Test retrieving a product with admin user"""
        self.client.login(user=self.admin_user)
        response = self.client.get(self.detail_url(self.product1.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_product_translations(self):
        """Test that product returns correct translation"""
        self.login(self.user2)
        response = self.client.get(self.detail_url(self.product1.id))

        product_data = response.data['data']
        # TranslatedFieldsReadMixin returns 'title' and 'description' (not language-suffixed)
        self.assertIn('title', product_data)
        self.assertIn('description', product_data)
        # Language-specific fields should not be in response
        self.assertNotIn('title_en', product_data)
        self.assertNotIn('title_uz', product_data)
        self.assertNotIn('description_en', product_data)
        self.assertNotIn('description_uz', product_data)

    def test_retrieve_nonexistent_product(self):
        """Test retrieving a product that doesn't exist"""
        self.login(self.user2)
        response = self.client.get(self.detail_url(99999))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_unavailable_product(self):
        """Test retrieving an unavailable product returns 404"""
        self.login(self.user2)
        response = self.client.get(self.detail_url(self.unavailable_product.id))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_product_response_structure(self):
        """Test the structure of product detail response"""
        self.login(self.user2)
        response = self.client.get(self.detail_url(self.product1.id))

        product_data = response.data['data']
        expected_fields = [
            'id', 'title', 'description', 'price',
            'discount_price', 'quantity', 'weight',
            'measurement', 'category', 'discount', 'in_stock'
        ]

        for field in expected_fields:
            self.assertIn(field, product_data)

    def test_retrieve_product_in_stock_status(self):
        """Test in_stock field is correctly calculated"""
        self.login(self.user2)
        response = self.client.get(self.detail_url(self.product1.id))

        self.assertTrue(response.data['data']['in_stock'])
        self.product1.quantity = 0
        self.product1.save()

        response = self.client.get(self.detail_url(self.product1.id))
        self.assertFalse(response.data['data']['in_stock'])

    def test_retrieve_product_discount_price_rounding(self):
        """Test that discount price is rounded to 2 decimal places"""
        self.login(self.user2)
        response = self.client.get(self.detail_url(self.product1.id))

        discount_price = response.data['data']['discount_price']
        # Check it's rounded to 2 decimal places
        self.assertEqual(len(str(discount_price).split('.')[-1]), 2)


class ProductRatingCreateAPIViewTest(ProductTestCase):
    """Tests for ProductRatingCreateAPIView"""

    def test_create_rating_with_admin_user(self):
        """Test creating a rating with admin user"""
        self.client.login(user=self.admin_user)
        data = {'rating': 4}

        response = self.client.post(self.rating_url(self.product1.id), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)  # CustomResponse returns 200
        self.assertTrue(
            ProductRating.objects.filter(
                user=self.admin_user,
                product=self.product1,
                rating=4
            ).exists()
        )

    def test_create_rating_with_authenticated_user(self):
        """Test creating a rating with authenticated user"""
        self.login(self.user2)
        data = {'rating': 4}

        response = self.client.post(self.rating_url(self.product1.id), data)

        # CustomResponse may return 200 instead of 201
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        self.assertTrue(
            ProductRating.objects.filter(
                user=self.user2,
                product=self.product1,
                rating=4
            ).exists()
        )

    def test_create_duplicate_rating(self):
        """Test that user cannot rate same product twice"""
        self.login(self.user2)
        data = {'rating': 4}

        # This should fail because self.user already rated product2 in setUp
        response = self.client.post(self.rating_url(self.product2.id), data)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_create_rating_invalid_rating_value(self):
        """Test creating rating with invalid value"""
        self.login(self.user2)

        # Test rating > 5
        data = {'rating': 6}
        response = self.client.post(self.rating_url(self.product1.id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test rating < 1
        data = {'rating': 0}
        response = self.client.post(self.rating_url(self.product1.id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_rating_missing_rating_field(self):
        """Test creating rating without rating field"""
        self.login(self.user2)
        data = {}

        response = self.client.post(self.rating_url(self.product1.id), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_rating_nonexistent_product(self):
        """Test creating rating for non-existent product"""
        self.client.login(user=self.admin_user)
        data = {'rating': 5}

        response = self.client.post(self.rating_url(99999), data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_rating_unavailable_product(self):
        """Test creating rating for unavailable product"""
        self.client.login(user=self.admin_user)
        data = {'rating': 5}

        response = self.client.post(self.rating_url(self.unavailable_product.id), data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_rating_without_authentication(self):
        """Test creating rating without any authentication"""
        data = {'rating': 5}
        response = self.client.post(self.rating_url(self.product1.id), data)

        # Should fail without authentication
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_create_rating_response_structure(self):
        """Test the structure of rating creation response"""
        self.login(self.user2)
        data = {'rating': 5}

        response = self.client.post(self.rating_url(self.product1.id), data)

        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        self.assertIn('data', response.data)
        rating_data = response.data['data']
        self.assertIn('rating', rating_data)
        self.assertEqual(rating_data['rating'], 5)


class ProductModelTest(ProductTestCase):
    """Tests for Product model methods"""

    def test_in_stock_method(self):
        """Test in_stock method"""
        self.assertTrue(self.product1.in_stock())

        self.product1.quantity = 0
        self.product1.save()
        self.assertFalse(self.product1.in_stock())

    def test_discount_price_property(self):
        """Test discount_price property calculation"""
        # Product1: price=100, discount=10%
        expected = Decimal("90.00")
        self.assertEqual(self.product1.discount_price, expected)

        # Product2: price=200, discount=20%
        expected = Decimal("160.00")
        self.assertEqual(self.product2.discount_price, expected)

    def test_product_creation_with_translations(self):
        """Test creating product with both language translations"""
        product = Product.objects.create(
            title_en="English Title",
            title_uz="Uzbek Sarlavha",
            description_en="English description text that is long enough",
            description_uz="Uzbek tavsif matni yetarlicha uzun bo'lishi kerak",
            price=Decimal("50.00"),
            quantity=5
        )

        self.assertEqual(product.title_en, "English Title")
        self.assertEqual(product.title_uz, "Uzbek Sarlavha")
        self.assertEqual(product.description_en, "English description text that is long enough")
        self.assertEqual(product.description_uz, "Uzbek tavsif matni yetarlicha uzun bo'lishi kerak")

class ProductTranslationTest(ProductTestCase):
    """Tests specifically for translation functionality"""

    def test_product_has_translation_fields(self):
        """Test that product has translation fields in database"""
        # Check that the product has language-specific fields
        self.assertTrue(hasattr(self.product1, 'title_en'))
        self.assertTrue(hasattr(self.product1, 'title_uz'))
        self.assertTrue(hasattr(self.product1, 'description_en'))
        self.assertTrue(hasattr(self.product1, 'description_uz'))

    def test_translation_fields_are_saved(self):
        """Test that translation fields are properly saved"""
        self.assertEqual(self.product1.title_en, "Test Product 1")
        self.assertEqual(self.product1.title_uz, "Test Mahsulot 1")
        self.assertEqual(self.product1.description_uz, "Bu test mahsulot tavsifi 30 belgidan ortiq bo'lishi kerak")

    def test_serializer_returns_single_title_field(self):
        """Test that serializer returns 'title' not 'title_en' or 'title_uz'"""
        self.login(self.user2)
        response = self.client.get(self.detail_url(self.product1.id))

        product_data = response.data['data']
        # Should have 'title' field
        self.assertIn('title', product_data)
        # Should NOT have language-specific fields in API response
        self.assertNotIn('title_en', product_data)
        self.assertNotIn('title_uz', product_data)

    def test_list_serializer_hides_translation_fields(self):
        """Test that list endpoint hides language-specific fields"""
        self.login(self.user2)
        response = self.client.get(self.list_url)

        results = response.data['data']['results']
        product = results[0]
        # Should return only 'title', not language variations
        self.assertIn('title', product)
        self.assertNotIn('title_en', product)
        self.assertNotIn('title_uz', product)


class ProductRatingModelTest(ProductTestCase):
    """Tests for ProductRating model"""

    def test_rating_creation(self):
        """Test creating a product rating"""
        rating = ProductRating.objects.create(
            user=self.user2,
            product=self.product1,
            rating=4
        )

        self.assertEqual(rating.rating, 4)
        self.assertEqual(rating.user, self.user2)
        self.assertEqual(rating.product, self.product1)

    def test_rating_str_method(self):
        """Test __str__ method of ProductRating"""
        rating = ProductRating.objects.create(
            user=self.user,
            product=self.product1,
            rating=5
        )

        # Product.title is used in __str__, not title_en
        expected = f"{self.user.first_name if self.user.first_name else 'unknown'} - {self.product1.title}-5"
        self.assertEqual(str(rating), expected)

    def test_rating_validation_constraints(self):
        """Test rating validators work correctly"""
        from django.core.exceptions import ValidationError

        # Valid rating
        rating = ProductRating(user=self.user2, product=self.product1, rating=3)
        rating.full_clean()  # Should not raise

        # Invalid rating (too high)
        rating_high = ProductRating(user=self.user2, product=self.product1, rating=6)
        with self.assertRaises(ValidationError):
            rating_high.full_clean()

        # Invalid rating (too low)
        rating_low = ProductRating(user=self.user2, product=self.product1, rating=0)
        with self.assertRaises(ValidationError):
            rating_low.full_clean()
