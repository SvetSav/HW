import os
import shutil
import tempfile
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from catalog.forms import FORBIDDEN_WORDS, ProductForm
from catalog.models import Category, Product

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp()


def create_test_image(fmt="JPEG", size=(100, 100), color=(255, 0, 0), name=None):
    """Создаёт валидное изображение в памяти."""
    img = Image.new("RGB", size, color=color)
    buf = BytesIO()
    img.save(buf, format=fmt)
    if name is None:
        name = f"test.{fmt.lower()}"
    return SimpleUploadedFile(name, buf.getvalue(), content_type=f"image/{fmt.lower()}")


def create_large_image():
    """PNG > 5 МБ через случайные данные (плохо сжимаются)."""
    data = os.urandom(1600 * 1600 * 3)  # ~7.3 МБ сырых данных
    img = Image.frombytes("RGB", (1600, 1600), data)
    buf = BytesIO()
    img.save(buf, format="PNG", compress_level=0)
    return SimpleUploadedFile("large.png", buf.getvalue(), content_type="image/png")


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ProductFormValidationTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Электроника", description="Разное"
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def _data(self, **overrides):
        data = {
            "name": "Ноутбук",
            "description": "Хороший ноутбук",
            "category": self.category.id,
            "price": "1000.00",
        }
        data.update(overrides)
        return data

    # ---- Запрещённые слова: разные регистры ----
    def test_forbidden_word_in_name_lowercase(self):
        form = ProductForm(data=self._data(name="казино рулит"))
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("запрещённое слово", form.errors["name"][0].lower())

    def test_forbidden_word_in_name_uppercase(self):
        form = ProductForm(data=self._data(name="КАЗИНО"))
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_forbidden_word_in_name_mixed_case(self):
        form = ProductForm(data=self._data(name="КаЗиНо"))
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_forbidden_word_in_description(self):
        form = ProductForm(data=self._data(description="Лучшее казино города"))
        self.assertFalse(form.is_valid())
        self.assertIn("description", form.errors)

    def test_all_forbidden_words_are_caught(self):
        for word in FORBIDDEN_WORDS:
            with self.subTest(word=word):
                form = ProductForm(data=self._data(name=f"Товар {word} здесь"))
                self.assertFalse(form.is_valid(), f'Слово "{word}" не было обнаружено')

    # ---- Цена ----
    def test_negative_price_is_rejected(self):
        form = ProductForm(data=self._data(price="-10.00"))
        self.assertFalse(form.is_valid())
        self.assertIn("price", form.errors)

    def test_zero_price_is_rejected(self):
        form = ProductForm(data=self._data(price="0"))
        self.assertFalse(form.is_valid())
        self.assertIn("price", form.errors)

    def test_positive_price_is_accepted(self):
        form = ProductForm(data=self._data(price="10.00"))
        self.assertTrue(form.is_valid(), form.errors)

    # ---- Изображение ----
    def test_valid_jpeg_image(self):
        form = ProductForm(
            data=self._data(), files={"image": create_test_image("JPEG")}
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_png_image(self):
        form = ProductForm(data=self._data(), files={"image": create_test_image("PNG")})
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_image_format(self):
        gif = create_test_image("GIF", name="test.gif")
        form = ProductForm(data=self._data(), files={"image": gif})
        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)

    def test_image_too_large(self):
        big = create_large_image()
        self.assertGreater(
            big.size, 5 * 1024 * 1024, "Тестовое изображение меньше 5 МБ"
        )
        form = ProductForm(data=self._data(), files={"image": big})
        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)

    # ---- Валидные данные целиком ----
    def test_valid_form(self):
        form = ProductForm(data=self._data())
        self.assertTrue(form.is_valid(), form.errors)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ProductCRUDTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Электроника", description="...")
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        self.product = Product.objects.create(
            name="Смартфон",
            description="Мощный",
            category=self.category,
            price=50000,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    # ---- Публичный доступ ----
    def test_home_page_public(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Смартфон")

    # ---- Анонимы получают редирект ----
    def test_create_requires_login(self):
        response = self.client.get(reverse("add_product"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_detail_requires_login(self):
        response = self.client.get(reverse("product_detail", args=[self.product.pk]))
        self.assertEqual(response.status_code, 302)

    def test_update_requires_login(self):
        response = self.client.get(reverse("product_update", args=[self.product.pk]))
        self.assertEqual(response.status_code, 302)

    def test_delete_requires_login(self):
        response = self.client.get(reverse("product_delete", args=[self.product.pk]))
        self.assertEqual(response.status_code, 302)

    # ---- CRUD под авторизацией ----
    def _login(self):
        self.assertTrue(
            self.client.login(email="test@example.com", password="testpass123")
        )

    def test_authenticated_create(self):
        self._login()
        response = self.client.post(
            reverse("add_product"),
            {
                "name": "Планшет",
                "description": "Новый",
                "category": self.category.id,
                "price": "30000",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(name="Планшет").exists())

    def test_authenticated_read(self):
        self._login()
        response = self.client.get(reverse("product_detail", args=[self.product.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Смартфон")

    def test_authenticated_update_redirects_to_detail(self):
        self._login()
        response = self.client.post(
            reverse("product_update", args=[self.product.pk]),
            {
                "name": "Смартфон Pro",
                "description": "Обновлённый",
                "category": self.category.id,
                "price": "55000",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(f"/product/{self.product.pk}/", response.url)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Смартфон Pro")

    def test_authenticated_delete(self):
        self._login()
        response = self.client.post(reverse("product_delete", args=[self.product.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())
