from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

class Kolbasa(models.Model):
    """Модель колбасы с валидацией и вычисляемым свойством."""

    # Константы для поля kind
    KIND_CHOICES = [
        ('варёная', 'Варёная'),
        ('копчёная', 'Копчёная'),
        ('сырокопчёная', 'Сырокопчёная'),
        ('полукопчёная', 'Полукопчёная'),
        ('вяленая', 'Вяленая'),
    ]

    brand = models.CharField(
        max_length=100,
        verbose_name='Бренд',
        help_text='Непустая строка'
    )
    kind = models.CharField(
        max_length=20,
        choices=KIND_CHOICES,
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

    class Meta:
        verbose_name = 'Колбаса'
        verbose_name_plural = 'Колбасы'

    def clean(self):
        """Пользовательская валидация модели."""
        super().clean()

        # Проверка brand на непустую строку (хотя CharField уже требует строку, но может быть пробелы)
        if not self.brand or not self.brand.strip():
            raise ValidationError({'brand': 'Бренд не может быть пустым или состоять только из пробелов.'})

        # Приведение kind к нижнему регистру (если вдруг передали с другим регистром)
        if self.kind:
            self.kind = self.kind.lower()
            # Проверка допустимости значения (choices уже ограничивает, но можно и явно)
            allowed = [choice[0] for choice in self.KIND_CHOICES]
            if self.kind not in allowed:
                raise ValidationError({'kind': f'Неверный тип. Допустимые: {", ".join(allowed)}'})

        # Проверка weight диапазона (уже есть валидаторы, но можно дополнить)
        if self.weight < 50 or self.weight > 5000:
            raise ValidationError({'weight': 'Вес должен быть от 50 до 5000 грамм.'})

        # Логика поля num_of_slices в зависимости от precut
        if self.precut:
            if self.num_of_slices is None:
                raise ValidationError({'num_of_slices': 'Для нарезки обязательно укажите количество кусочков.'})
            if self.num_of_slices <= 0:
                raise ValidationError({'num_of_slices': 'Количество кусочков должно быть положительным.'})
        else:
            # Если не нарезка, сбрасываем num_of_slices в None
            if self.num_of_slices is not None:
                self.num_of_slices = None

    def save(self, *args, **kwargs):
        """Переопределяем save для применения clean() перед сохранением."""
        self.full_clean()  # вызывает clean() и валидацию полей
        super().save(*args, **kwargs)

    @property
    def weight_per_slice(self) -> float:
        """Вес одного кусочка, если колбаса нарезана."""
        if not self.precut:
            raise ValueError("Эта колбаса - не нарезка")
        if self.num_of_slices is None or self.num_of_slices == 0:
            raise ValueError("Некорректное количество кусочков")
        return self.weight / self.num_of_slices

    def __str__(self):
        return f"{self.brand} ({self.kind}) - {self.weight}г"
    