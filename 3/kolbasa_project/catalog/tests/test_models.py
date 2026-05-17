from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from ..models import Kind, Kolbasa

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
        """Артикул должен быть уникальным (проверка на уровне БД)."""
        # Проверка Python-валидации
        dup = Kolbasa(
            article='ART001',  # уже существует
            brand='Дубликат',
            kind=self.kind_varenaya,
            weight=500,
        )
        with self.assertRaises(ValidationError):
            dup.full_clean()

        # Проверка ограничения БД
        dup2 = Kolbasa(
            article='ART001',
            brand='Дубликат',
            kind_id=self.kind_varenaya.pk,  # передаём ID, чтобы избежать доп. запросов
            weight=500,
        )
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                dup2.save_base(raw=True)   # здесь упадёт IntegrityError

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