from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

class Kind(models.Model):
    """Тип колбасы (варёная, копчёная и т.д.)."""
    name = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Название типа'
    )

    class Meta:
        verbose_name = 'Тип колбасы'
        verbose_name_plural = 'Типы колбас'
        ordering = ['name']

    def __str__(self):
        return self.name

class KolbasaManager(models.Manager):
    def by_type(self, kind_name):
        """Возвращает колбасы заданного типа (по названию)."""
        return self.filter(kind__name__iexact=kind_name)

    def heavy(self, min_weight=1000):
        """Возвращает колбасы тяжелее указанного веса (по умолчанию 1000 г)."""
        return self.filter(weight__gte=min_weight)

class Kolbasa(models.Model):
    """Модель колбасы с расширенными возможностями."""

    article = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Артикул'
    )
    brand = models.CharField(
        max_length=100,
        verbose_name='Бренд'
    )
    kind = models.ForeignKey(
        Kind,
        on_delete=models.PROTECT,
        related_name='kolbasas',
        verbose_name='Тип колбасы'
    )
    weight = models.PositiveIntegerField(
        validators=[
            MinValueValidator(50),
            MaxValueValidator(5000)
        ],
        verbose_name='Вес (г)',
        help_text='От 50 до 5000 грамм'
    )
    precut = models.BooleanField(
        default=False,
        verbose_name='Нарезка'
    )
    num_of_slices = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Количество кусочков',
        help_text='Только если колбаса нарезана'
    )

    objects = KolbasaManager()

    class Meta:
        verbose_name = 'Колбаса'
        verbose_name_plural = 'Колбасы'
        ordering = ['brand']
        constraints = [
            models.CheckConstraint(
                check=models.Q(weight__gte=50) & models.Q(weight__lte=5000),
                name='weight_between_50_and_5000'
            )
        ]

    def clean(self):
        super().clean()
        # Проверка brand на непустоту
        if not self.brand or not self.brand.strip():
            raise ValidationError({'brand': 'Бренд не может быть пустым.'})
        # Логика поля num_of_slices
        if self.precut:
            if self.num_of_slices is None:
                raise ValidationError({'num_of_slices': 'Для нарезки укажите количество кусочков.'})
            if self.num_of_slices <= 0:
                raise ValidationError({'num_of_slices': 'Количество кусочков должно быть положительным.'})
        else:
            if self.num_of_slices is not None:
                self.num_of_slices = None

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def weight_per_slice(self) -> float:
        """Вес одного кусочка (если нарезана)."""
        if not self.precut:
            raise ValueError("Эта колбаса - не нарезка")
        if self.num_of_slices is None or self.num_of_slices == 0:
            raise ValueError("Некорректное количество кусочков")
        return self.weight / self.num_of_slices

    @property
    def is_heavy(self) -> bool:
        """Является ли колбаса тяжёлой (вес > 1000 г)."""
        return self.weight > 1000

    def __str__(self):
        return f"{self.article} - {self.brand} ({self.kind})"