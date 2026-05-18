from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Kind, Kolbasa, Cart, CartItem

class RoleBasedAccessTests(TestCase):
    """Тесты ролевой модели, прав доступа и корзины."""

    @classmethod
    def setUpTestData(cls):
        # 1. Типы и товары
        cls.kind_varenaya = Kind.objects.create(name='варёная')
        cls.kind_kopch = Kind.objects.create(name='копчёная')
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

        # 2. Контент-типы и права
        kolbasa_ct = ContentType.objects.get_for_model(Kolbasa)
        cart_ct = ContentType.objects.get_for_model(Cart)
        cartitem_ct = ContentType.objects.get_for_model(CartItem)

        tovaroved_group, _ = Group.objects.get_or_create(name='Товаровед')
        tovaroved_perms = Permission.objects.filter(
            content_type=kolbasa_ct,
            codename__in=['add_kolbasa', 'change_kolbasa', 'delete_kolbasa', 'view_kolbasa']
        )
        tovaroved_group.permissions.set(tovaroved_perms)

        manager_group, _ = Group.objects.get_or_create(name='Менеджер по продажам')
        manager_perms = list(Permission.objects.filter(
            content_type__in=[cart_ct, cartitem_ct],
            codename__in=['add_cart', 'change_cart', 'delete_cart', 'view_cart',
                          'add_cartitem', 'change_cartitem', 'delete_cartitem', 'view_cartitem']
        ))
        manager_perms.append(Permission.objects.get(content_type=kolbasa_ct, codename='view_kolbasa'))
        manager_group.permissions.set(manager_perms)

        # 3. Пользователи
        cls.guest = User.objects.create_user(username='guest', password='testpass')
        cls.tovaroved = User.objects.create_user(username='tovaroved', password='testpass')
        cls.tovaroved.groups.add(tovaroved_group)
        cls.manager1 = User.objects.create_user(username='manager1', password='testpass')
        cls.manager1.groups.add(manager_group)
        cls.manager2 = User.objects.create_user(username='manager2', password='testpass')
        cls.manager2.groups.add(manager_group)

    # ================================================================
    # Тесты доступности страниц для разных ролей
    # ================================================================
    def test_guest_can_view_product_list(self):
        url = reverse('product_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_guest_can_view_product_detail(self):
        url = reverse('product_detail', args=[self.product1.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_guest_cannot_access_create_product(self):
        self.client.login(username='guest', password='testpass')
        url = reverse('product_create')
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 403])

    def test_guest_cannot_access_cart(self):
        self.client.login(username='guest', password='testpass')
        url = reverse('cart_detail')
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 403])

    def test_tovaroved_can_access_create_product(self):
        self.client.login(username='tovaroved', password='testpass')
        url = reverse('product_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_tovaroved_cannot_access_cart(self):
        self.client.login(username='tovaroved', password='testpass')
        url = reverse('cart_detail')
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 403])

    def test_manager_can_access_cart(self):
        self.client.login(username='manager1', password='testpass')
        url = reverse('cart_detail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_manager_cannot_access_create_product(self):
        self.client.login(username='manager1', password='testpass')
        url = reverse('product_create')
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 403])

    # ================================================================
    # Тесты корзины: добавление, расчёт цен, изоляция
    # ================================================================
    def test_add_to_cart_applies_small_opt_price(self):
        self.client.login(username='manager1', password='testpass')
        url = reverse('add_to_cart', args=[self.product1.pk])
        response = self.client.post(url, {'quantity': 10})
        self.assertRedirects(response, reverse('cart_detail'))
        cart = Cart.objects.get(user=self.manager1, status='draft')
        item = cart.items.get(product=self.product1)
        self.assertEqual(item.price, self.product1.price_small_opt)
        self.assertEqual(item.quantity, 10)

    def test_add_to_cart_applies_large_opt_price(self):
        self.client.login(username='manager1', password='testpass')
        url = reverse('add_to_cart', args=[self.product1.pk])
        self.client.post(url, {'quantity': 50})
        cart = Cart.objects.get(user=self.manager1, status='draft')
        item = cart.items.get(product=self.product1)
        self.assertEqual(item.price, self.product1.price_large_opt)

    def test_add_to_cart_default_unit_price(self):
        self.client.login(username='manager1', password='testpass')
        url = reverse('add_to_cart', args=[self.product1.pk])
        self.client.post(url, {'quantity': 2})
        cart = Cart.objects.get(user=self.manager1, status='draft')
        item = cart.items.get(product=self.product1)
        self.assertEqual(item.price, self.product1.price_unit)

    def test_cart_total_sum_without_discount(self):
        self.client.login(username='manager1', password='testpass')
        self.client.post(reverse('add_to_cart', args=[self.product1.pk]), {'quantity': 5})
        self.client.post(reverse('add_to_cart', args=[self.product2.pk]), {'quantity': 2})
        cart = Cart.objects.get(user=self.manager1, status='draft')
        expected = 5 * 200 + 2 * 300  # 1000 + 600 = 1600
        self.assertEqual(cart.total_sum, expected)

    def test_cart_total_sum_with_discount(self):
        self.client.login(username='manager1', password='testpass')
        self.client.post(reverse('add_to_cart', args=[self.product1.pk]), {'quantity': 10})
        cart = Cart.objects.get(user=self.manager1, status='draft')
        self.assertEqual(cart.total_sum, 10 * 180)
        cart.discount_percent = 15
        cart.save()
        self.assertEqual(cart.total_sum, 10 * 180 * 0.85)

    def test_manager_cannot_modify_others_cart_item(self):
        cart1 = Cart.objects.create(user=self.manager1)
        item = CartItem.objects.create(cart=cart1, product=self.product1, quantity=1)
        self.client.login(username='manager2', password='testpass')
        url = reverse('remove_from_cart', args=[item.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(CartItem.objects.filter(pk=item.pk).exists())

    def test_manager_cannot_submit_others_cart(self):
        cart1 = Cart.objects.create(user=self.manager1)
        self.client.login(username='manager2', password='testpass')
        url = reverse('submit_cart')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_submitted_cart_immutable(self):
        self.client.login(username='manager1', password='testpass')
        cart = Cart.objects.create(user=self.manager1)
        CartItem.objects.create(cart=cart, product=self.product1, quantity=5)
        cart.status = 'submitted'
        cart.save()
        response = self.client.post(reverse('add_to_cart', args=[self.product2.pk]), {'quantity': 1})
        self.assertEqual(cart.items.count(), 1)
        self.assertTrue(Cart.objects.filter(user=self.manager1, status='draft').exists())

    def test_cart_list_shows_only_submitted(self):
        self.client.login(username='manager1', password='testpass')
        Cart.objects.create(user=self.manager1, status='draft')
        submitted = Cart.objects.create(user=self.manager1, status='submitted')
        response = self.client.get(reverse('cart_list'))
        self.assertEqual(response.status_code, 200)
        carts = response.context['carts']
        self.assertEqual(len(carts), 1)
        self.assertEqual(carts[0], submitted)