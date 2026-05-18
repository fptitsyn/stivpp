from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.urls import reverse
from ..models import Kind, Kolbasa, Cart

class KolbasaModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Создаём общие данные, которые не изменяются в тестах."""
        cls.kind_varenaya = Kind.objects.create(name='варёная')
        cls.kind_kopchenaya = Kind.objects.create(name='копчёная')
        # Создаём колбасы с обязательным полем price_unit
        cls.kolbasa1 = Kolbasa.objects.create(
            article='ART001',
            brand='Клинская',
            kind=cls.kind_varenaya,
            weight=400,
            precut=True,
            num_of_slices=8,
            price_unit=250.0
        )
        cls.kolbasa2 = Kolbasa.objects.create(
            article='ART002',
            brand='Черкизово',
            kind=cls.kind_kopchenaya,
            weight=1200,
            precut=False,
            price_unit=300.0
        )

    # 1. Тесты валидации полей
    def test_weight_validation_positive(self):
        """Вес должен быть в диапазоне 50-5000."""
        kolbasa = Kolbasa(
            article='TEST001',
            brand='Test',
            kind=self.kind_varenaya,
            weight=30,  # меньше минимума
            price_unit=100.0
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
            price_unit=100.0
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
            price_unit=100.0
        )
        with self.assertRaises(ValidationError):
            kolbasa.full_clean()

    # 2. Тест уникальности артикула
    def test_article_unique(self):
        """Артикул должен быть уникальным (проверка на уровне БД)."""
        # Проверка Python-валидации
        dup = Kolbasa(
            article='ART001',  # уже существует
            brand='Дубликат',
            kind=self.kind_varenaya,
            weight=500,
            price_unit=100.0
        )
        with self.assertRaises(ValidationError):
            dup.full_clean()

        # Проверка ограничения БД
        dup2 = Kolbasa(
            article='ART001',
            brand='Дубликат',
            kind_id=self.kind_varenaya.pk,
            weight=500,
            price_unit=100.0
        )
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                dup2.save_base(raw=True)

    # 3. Тест on_delete=PROTECT
    def test_kind_on_delete_protect(self):
        """Нельзя удалить тип колбасы, если есть связанные товары."""
        with self.assertRaises(IntegrityError):
            self.kind_varenaya.delete()

    # 4. Тест вычисляемого свойства weight_per_slice
    def test_weight_per_slice_property(self):
        """Правильный расчёт веса кусочка, если нарезка."""
        self.assertEqual(self.kolbasa1.weight_per_slice, 50.0)
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
            kind_id=self.kind_varenaya.pk,
            weight=10,  # недопустимый вес
            price_unit=100.0
        )
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                kolbasa.save_base(raw=True)

    # 9. Тест использования setUpTestData (проверяем, что данные созданы)
    def test_setup_test_data_created_correctly(self):
        """Проверка, что данные из setUpTestData доступны."""
        self.assertEqual(Kolbasa.objects.count(), 2)
        self.assertEqual(Kind.objects.count(), 2)

    # 10. Тест использования setUp (пример сброса состояния)
    def test_setup_resets_changes(self):
        """Изменения, сделанные в одном тесте, не влияют на другие."""
        self.kolbasa1.delete()
        self.assertEqual(Kolbasa.objects.count(), 1)

    # Дополнительный тест на валидацию при изменении precut
    def test_precut_change_resets_num_of_slices(self):
        """При смене precut с True на False num_of_slices сбрасывается."""
        kolbasa = Kolbasa.objects.get(article='ART001')
        self.assertTrue(kolbasa.precut)
        self.assertIsNotNone(kolbasa.num_of_slices)
        kolbasa.precut = False
        kolbasa.save()
        self.assertIsNone(kolbasa.num_of_slices)

    # ================================================================
    # Тесты корзины: добавление, расчёт цен, изоляция
    # ================================================================
    class CartModelTest(TestCase):

        @classmethod
        def setUpTestData(cls):
            """Создаём общие данные, которые не изменяются в тестах."""

            cls.product1 = Kolbasa.objects.create(
                article='TST-001',
                brand='Тестовая варёная',
                kind=cls.kind_varenaya,
                weight=500,
                precut=False,
                price_unit=200,
                price_small_opt=180,
                qty_small_opt=10,
                price_large_opt=150,
                qty_large_opt=50,
            )
            cls.product2 = Kolbasa.objects.create(
                article='TST-002',
                brand='Тестовая копчёная',
                kind=cls.kind_kopch,
                weight=300,
                precut=True,
                num_of_slices=6,
                price_unit=300,
                price_small_opt=None,
                qty_small_opt=None,
                price_large_opt=None,
                qty_large_opt=None,
            )

        def test_add_to_cart_applies_small_opt_price(self):
            """При добавлении количества >= мелкого опта применяется оптовая цена."""
            self.client.login(username='manager1', password='testpass')
            url = reverse('add_to_cart', args=[self.product1.pk])
            response = self.client.post(url, {'quantity': 10})
            self.assertRedirects(response, reverse('cart_detail'))

            cart = Cart.objects.get(user=self.manager1, status='draft')
            item = cart.items.get(product=self.product1)
            self.assertEqual(item.price, self.product1.price_small_opt)  # 180
            self.assertEqual(item.quantity, 10)

        def test_add_to_cart_applies_large_opt_price(self):
            """При количестве >= крупного опта цена ещё ниже."""
            self.client.login(username='manager1', password='testpass')
            url = reverse('add_to_cart', args=[self.product1.pk])
            self.client.post(url, {'quantity': 50})
            cart = Cart.objects.get(user=self.manager1, status='draft')
            item = cart.items.get(product=self.product1)
            self.assertEqual(item.price, self.product1.price_large_opt)  # 150

        def test_add_to_cart_default_unit_price(self):
            """При малом количестве цена за единицу."""
            self.client.login(username='manager1', password='testpass')
            url = reverse('add_to_cart', args=[self.product1.pk])
            self.client.post(url, {'quantity': 2})
            cart = Cart.objects.get(user=self.manager1, status='draft')
            item = cart.items.get(product=self.product1)
            self.assertEqual(item.price, self.product1.price_unit)  # 200

        def test_cart_total_sum_without_discount(self):
            """Расчёт суммы корзины без общей скидки."""
            self.client.login(username='manager1', password='testpass')
            # Добавим два товара: 5 шт product1 (200) и 2 шт product2 (300)
            self.client.post(reverse('add_to_cart', args=[self.product1.pk]), {'quantity': 5})
            self.client.post(reverse('add_to_cart', args=[self.product2.pk]), {'quantity': 2})
            cart = Cart.objects.get(user=self.manager1, status='draft')
            expected = 5 * 200 + 2 * 300  # 1000 + 600 = 1600
            self.assertEqual(cart.total_sum, expected)

        def test_cart_total_sum_with_discount(self):
            """Общая скидка применяется к сумме корзины."""
            self.client.login(username='manager1', password='testpass')
            self.client.post(reverse('add_to_cart', args=[self.product1.pk]), {'quantity': 10})
            cart = Cart.objects.get(user=self.manager1, status='draft')
            # 10 * 180 = 1800
            self.assertEqual(cart.total_sum, 1800)
            # Устанавливаем скидку 15%
            cart.discount_percent = 15
            cart.save()
            expected = 1800 * 0.85  # 1530
            self.assertEqual(cart.total_sum, expected)
