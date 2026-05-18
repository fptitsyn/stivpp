from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

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

    price_unit = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)], verbose_name='Цена за единицу (руб.)')
    price_small_opt = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0.01)], verbose_name='Цена мелкий опт (руб.)')
    price_large_opt = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0.01)], verbose_name='Цена крупный опт (руб.)')
    qty_small_opt = models.PositiveIntegerField(blank=True, null=True, verbose_name='Количество для мелкого опта')
    qty_large_opt = models.PositiveIntegerField(blank=True, null=True, verbose_name='Количество для крупного опта')

    objects = KolbasaManager()

    class Meta:
        verbose_name = 'Колбаса'
        verbose_name_plural = 'Колбасы'
        ordering = ['brand']
        constraints = [
            models.CheckConstraint(check=models.Q(weight__gte=50) & models.Q(weight__lte=5000), name='weight_between_50_and_5000')
        ]

    def clean(self):
        super().clean()
        if not self.brand or not self.brand.strip():
            raise ValidationError({'brand': 'Бренд не может быть пустым.'})
        if self.precut:
            if self.num_of_slices is None:
                raise ValidationError({'num_of_slices': 'Для нарезки укажите количество кусочков.'})
            if self.num_of_slices <= 0:
                raise ValidationError({'num_of_slices': 'Количество кусочков должно быть положительным.'})
        else:
            self.num_of_slices = None
        # Валидация оптовых цен
        if bool(self.price_small_opt) != bool(self.qty_small_opt):
            raise ValidationError('Укажите одновременно цену и количество для мелкого опта, либо оставьте оба пустыми.')
        if bool(self.price_large_opt) != bool(self.qty_large_opt):
            raise ValidationError('Укажите одновременно цену и количество для крупного опта, либо оставьте оба пустыми.')
        if self.price_small_opt and self.price_large_opt:
            if self.qty_small_opt >= self.qty_large_opt:
                raise ValidationError('Количество для крупного опта должно быть больше, чем для мелкого.')
            if self.price_small_opt <= self.price_large_opt:
                raise ValidationError('Цена крупного опта должна быть ниже мелкооптовой.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def weight_per_slice(self):
        if not self.precut:
            raise ValueError("Эта колбаса - не нарезка")
        return self.weight / self.num_of_slices

    @property
    def is_heavy(self):
        return self.weight > 1000

    def __str__(self):
        return f"{self.article} - {self.brand} ({self.kind})"


class Cart(models.Model):
    STATUS_CHOICES = [('draft', 'Черновик'), ('submitted', 'Отправлена')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts', verbose_name='Пользователь')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    discount_percent = models.PositiveIntegerField(default=0, verbose_name='Общая скидка (%)', help_text='0-100')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        ordering = ['-created_at']

    @property
    def total_sum(self):
        items_sum = sum(item.item_total for item in self.items.all())
        if self.discount_percent > 0:
            return items_sum * (100 - self.discount_percent) / 100
        return items_sum

    def __str__(self):
        return f"Корзина {self.id} ({self.user.username}) - {self.status}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name='Корзина')
    product = models.ForeignKey(Kolbasa, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за единицу')

    class Meta:
        verbose_name = 'Позиция корзины'
        verbose_name_plural = 'Позиции корзины'
        unique_together = ('cart', 'product')

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError({'quantity': 'Количество должно быть положительным.'})
        if self.cart.status != 'draft':
            raise ValidationError('Нельзя изменять позиции отправленной корзины.')

    def save(self, *args, **kwargs):
        if not self.pk:
            # Автоопределение цены
            self.price = self.product.price_unit
            if self.product.price_large_opt and self.quantity >= self.product.qty_large_opt:
                self.price = self.product.price_large_opt
            elif self.product.price_small_opt and self.quantity >= self.product.qty_small_opt:
                self.price = self.product.price_small_opt
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def item_total(self):
        return self.price * self.quantity
