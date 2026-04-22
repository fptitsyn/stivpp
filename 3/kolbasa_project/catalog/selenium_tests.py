from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .models import Kind, Kolbasa

class SeleniumTests(StaticLiveServerTestCase):
    """Тесты пользовательского интерфейса с Selenium."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        # Создаём тип колбасы и тестовый товар
        self.kind_varenaya = Kind.objects.create(name='варёная')
        self.kolbasa = Kolbasa.objects.create(
            article='TEST-SELENIUM-001',
            brand='Тестовая колбаса',
            kind=self.kind_varenaya,
            weight=500,
            precut=True,
            num_of_slices=10
        )

    def test_navigation_to_about_page(self):
        """Переход со списка товаров на страницу «О сервисе»."""
        self.driver.get(f'{self.live_server_url}/')
        try:
            # Пробуем найти ссылку с точным текстом
            about_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, 'О сервисе'))
            )
        except TimeoutException:
            # Если не нашли точный текст, ищем по частичному совпадению
            try:
                about_link = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, 'сервис'))
                )
            except TimeoutException:
                self.fail("Ссылка 'О сервисе' не найдена на главной странице.")
        about_link.click()
        WebDriverWait(self.driver, 10).until(
            EC.url_contains('/about/')
        )
        heading = self.driver.find_element(By.TAG_NAME, 'h1')
        self.assertIn('О нашем сервисе', heading.text)
        self.assertIn('О нашем сервисе', self.driver.title)

    def test_product_detail_has_heading(self):
        """Детальная страница содержит заголовок с названием товара и информацию о весе."""
        detail_url = f'{self.live_server_url}/product/{self.kolbasa.pk}/'
        self.driver.get(detail_url)

        # Ищем любой заголовок (h1 или h2), содержащий название товара
        try:
            heading = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[self::h1 or self::h2][contains(., 'Тестовая колбаса')]")
                )
            )
        except TimeoutException:
            print("Текущий URL:", self.driver.current_url)
            self.fail("Заголовок с названием товара не найден!")

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
        try:
            link = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.LINK_TEXT, 'О сервисе'))
            )
        except TimeoutException:
            link = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'сервис'))
            )
        href = link.get_attribute('href')
        self.assertEqual(href, f'{self.live_server_url}/about/')