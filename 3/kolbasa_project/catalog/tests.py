from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from .models import Kind, Kolbasa

class SeleniumTests(StaticLiveServerTestCase):
    """Тесты пользовательского интерфейса с Selenium."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        self.kolbasa = Kolbasa.objects.create(
            brand='Тестовая колбаса',
            kind='варёная',
            weight=500,
            precut=True,
            num_of_slices=10
        )

    def test_navigation_to_about_page(self):
        """Переход со списка товаров на страницу «О сервисе»."""
        self.driver.get(f'{self.live_server_url}/')
        about_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, 'О сервисе'))
        )
        about_link.click()
        WebDriverWait(self.driver, 10).until(
            EC.url_contains('/about/')
        )
        heading = self.driver.find_element(By.TAG_NAME, 'h1')
        self.assertIn('О нашем сервисе', heading.text)
        self.assertIn('О нашем сервисе', self.driver.title)

    def test_product_detail_has_heading(self):
        """Детальная страница содержит заголовок h2 с названием и информацию о весе."""
        detail_url = f'{self.live_server_url}/product/{self.kolbasa.pk}/'
        self.driver.get(detail_url)

        # Заголовок h2 с названием товара
        try:
            heading = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//h2[contains(., 'Тестовая колбаса')]")
                )
            )
        except TimeoutException:
            print("Текущий URL:", self.driver.current_url)
            print("HTML (первые 1000 символов):", self.driver.page_source[:1000])
            self.fail("Заголовок h2 с названием товара не найден!")

        # Элемент с текстом "Вес:"
        try:
            weight_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(., 'Вес:')]")
                )
            )
            self.assertIn('500 г', weight_element.text)
        except TimeoutException:
            self.fail("Элемент с текстом 'Вес:' не найден!")

        # Вес кусочка
        try:
            slice_elem = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(., 'Вес одного кусочка:')]")
                )
            )
            self.assertIn('50.00 г', slice_elem.text)
        except TimeoutException:
            self.fail("Элемент с текстом 'Вес одного кусочка:' не найден!")

    def test_about_page_accessible_from_list(self):
        """На странице списка есть ссылка 'О сервисе'."""
        self.driver.get(f'{self.live_server_url}/')
        link = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'О сервисе'))
        )
        self.assertEqual(link.get_attribute('href'), f'{self.live_server_url}/about/')


class KolbasaModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Создаём общие данные, которые не изменяются в тестах."""
        cls.kind_varenaya = Kind.objects.create(name='варёная')
        cls.kind_kopchenaya = Kind.objects.create(name='копчёная')
        # Создадим одну колбасу для тестов менеджеров
        cls.kolbasa1 = Kolbasa.objects.create(
            article='ART001',
            brand='Клинская',
            kind=cls.kind_varenaya,
            weight=400,
            precut=True,
            num_of_slices=8
        )
        cls.kolbasa2 = Kolbasa.objects.create(
            article='ART002',
            brand='Черкизово',
            kind=cls.kind_kopchenaya,
            weight=1200,
            precut=False,
        )

    def setUp(self):
        """Сбрасываем изменяемые данные перед каждым тестом."""
        # Убедимся, что в тестах менеджеров не появляется лишних записей
        pass

    # 1. Тесты валидации полей
    def test_weight_validation_positive(self):
        """Вес должен быть в диапазоне 50-5000."""
        kolbasa = Kolbasa(
            article='TEST001',
            brand='Test',
            kind=self.kind_varenaya,
            weight=30,  # меньше минимума
        )
        with self.assertRaises(ValidationError):
            kolbasa.full_clean()

        kolbasa.weight = 6000  # больше максимума
        with self.assertRaises(ValidationError):
            kolbasa.full_clean()

    def test_num_of_slices_validation(self):
        """Если precut=True, num_of_slices обязательно и положительно."""
        kolbasa = Kolbasa(
            article='TEST002',
            brand='Test',
            kind=self.kind_varenaya,
            weight=500,
            precut=True,
            # num_of_slices не указано
        )
        with self.assertRaises(ValidationError):
            kolbasa.full_clean()

        kolbasa.num_of_slices = -5
        with self.assertRaises(ValidationError):
            kolbasa.full_clean()

    def test_brand_not_empty(self):
        """Бренд не может быть пустым или состоять из пробелов."""
        kolbasa = Kolbasa(
            article='TEST003',
            brand='   ',
            kind=self.kind_varenaya,
            weight=500,
        )
        with self.assertRaises(ValidationError):
            kolbasa.full_clean()

    # 2. Тест уникальности артикула
    def test_article_unique(self):
        """Артикул должен быть уникальным."""
        kolbasa_dup = Kolbasa(
            article='ART001',  # уже существует
            brand='Дубликат',
            kind=self.kind_varenaya,
            weight=500,
        )
        with self.assertRaises(ValidationError):
            kolbasa_dup.full_clean()
        # Проверка на уровне БД (IntegrityError при прямом сохранении без full_clean)
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Kolbasa.objects.create(
                    article='ART001',
                    brand='Дубликат',
                    kind=self.kind_varenaya,
                    weight=500,
                )

    # 3. Тест on_delete=PROTECT
    def test_kind_on_delete_protect(self):
        """Нельзя удалить тип колбасы, если есть связанные товары."""
        with self.assertRaises(IntegrityError):
            self.kind_varenaya.delete()

    # 4. Тест вычисляемого свойства weight_per_slice
    def test_weight_per_slice_property(self):
        """Правильный расчёт веса кусочка, если нарезка."""
        self.assertEqual(self.kolbasa1.weight_per_slice, 50.0)  # 400/8 = 50
        with self.assertRaises(ValueError):
            _ = self.kolbasa2.weight_per_slice  # не нарезка

    # 5. Тест второго вычисляемого свойства is_heavy
    def test_is_heavy_property(self):
        """Колбаса считается тяжёлой при весе > 1000 г."""
        self.assertFalse(self.kolbasa1.is_heavy)   # 400 г
        self.assertTrue(self.kolbasa2.is_heavy)    # 1200 г

    # 6. Тест менеджера by_type
    def test_manager_by_type(self):
        """Менеджер возвращает колбасы заданного типа."""
        varenaya_qs = Kolbasa.objects.by_type('варёная')
        self.assertEqual(varenaya_qs.count(), 1)
        self.assertEqual(varenaya_qs.first(), self.kolbasa1)

        kopchenaya_qs = Kolbasa.objects.by_type('копчёная')
        self.assertEqual(kopchenaya_qs.count(), 1)
        self.assertEqual(kopchenaya_qs.first(), self.kolbasa2)

        # Регистронезависимость
        self.assertEqual(Kolbasa.objects.by_type('ВАРЁНАЯ').count(), 1)

    # 7. Тест менеджера heavy
    def test_manager_heavy(self):
        """Менеджер возвращает колбасы тяжелее указанного веса."""
        heavy_qs = Kolbasa.objects.heavy(1000)
        self.assertEqual(heavy_qs.count(), 1)
        self.assertEqual(heavy_qs.first(), self.kolbasa2)

        heavy_qs_all = Kolbasa.objects.heavy(300)
        self.assertEqual(heavy_qs_all.count(), 2)

    # 8. Тест CheckConstraint на уровне БД
    def test_check_constraint_weight_range(self):
        """Попытка сохранить колбасу с весом вне [50,5000] вызывает IntegrityError."""
        kolbasa = Kolbasa(
            article='TEST004',
            brand='Test',
            kind=self.kind_varenaya,
            weight=10,  # недопустимый вес
        )
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                kolbasa.save()  # full_clean не вызывается, constraint должен сработать

    # 9. Тест использования setUpTestData (проверяем, что данные созданы)
    def test_setup_test_data_created_correctly(self):
        """Проверка, что данные из setUpTestData доступны."""
        self.assertEqual(Kolbasa.objects.count(), 2)
        self.assertEqual(Kind.objects.count(), 2)

    # 10. Тест использования setUp (пример сброса состояния)
    def test_setup_resets_changes(self):
        """Изменения, сделанные в одном тесте, не влияют на другие."""
        # Удалим одну колбасу
        self.kolbasa1.delete()
        self.assertEqual(Kolbasa.objects.count(), 1)
        # В следующем тесте count снова будет 2, потому что setUpTestData пересоздаёт данные для каждого теста

    # Дополнительный тест на валидацию при изменении precut
    def test_precut_change_resets_num_of_slices(self):
        """При смене precut с True на False num_of_slices сбрасывается."""
        kolbasa = Kolbasa.objects.get(article='ART001')
        self.assertTrue(kolbasa.precut)
        self.assertIsNotNone(kolbasa.num_of_slices)
        kolbasa.precut = False
        kolbasa.save()
        self.assertIsNone(kolbasa.num_of_slices)