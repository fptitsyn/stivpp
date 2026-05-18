from django.test import TestCase
from django.urls import reverse
from catalog.models import Kind, Kolbasa

class ContentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.kind_varenaya = Kind.objects.create(name='варёная')
        cls.kind_kopch = Kind.objects.create(name='копчёная')
        cls.k1 = Kolbasa.objects.create(
            article='C001', brand='Альфа', kind=cls.kind_varenaya,
            weight=300, precut=False, price_unit=150.0
        )
        cls.k2 = Kolbasa.objects.create(
            article='C002', brand='Бета', kind=cls.kind_kopch,
            weight=1200, precut=True, num_of_slices=12, price_unit=200.0
        )
        cls.k3 = Kolbasa.objects.create(
            article='C003', brand='Гамма', kind=cls.kind_varenaya,
            weight=150, precut=True, num_of_slices=5, price_unit=100.0
        )

    def test_product_list_template(self):
        url = reverse('product_list')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'catalog/product_list.html')

    def test_product_list_contains_objects(self):
        url = reverse('product_list')
        response = self.client.get(url)
        self.assertTrue('kolbasas' in response.context)
        self.assertEqual(len(response.context['kolbasas']), 3)

    def test_product_list_sort_by_brand(self):
        url = reverse('product_list') + '?sort=brand'
        response = self.client.get(url)
        brands = [k.brand for k in response.context['kolbasas']]
        self.assertEqual(brands, ['Альфа', 'Бета', 'Гамма'])

    def test_product_list_sort_by_weight(self):
        url = reverse('product_list') + '?sort=weight'
        response = self.client.get(url)
        weights = [k.weight for k in response.context['kolbasas']]
        self.assertEqual(weights, [150, 300, 1200])

    def test_product_list_sort_by_kind(self):
        url = reverse('product_list') + '?sort=kind'
        response = self.client.get(url)
        kinds = [k.kind.name for k in response.context['kolbasas']]
        self.assertEqual(kinds, ['варёная', 'варёная', 'копчёная'])

    def test_product_list_sort_by_num_slices(self):
        url = reverse('product_list') + '?sort=num_slices'
        response = self.client.get(url)
        slices = [k.num_of_slices for k in response.context['kolbasas']]
        self.assertEqual(slices, [None, 5, 12])

    def test_about_page_contains_text(self):
        url = reverse('about')
        response = self.client.get(url)
        self.assertContains(response, 'О нашем сервисе')

    # TC-03
    def test_product_list_filter_by_kind(self):
        url = reverse('product_list') + f'?kind={self.kind_varenaya.pk}'
        response = self.client.get(url)
        qs = response.context['kolbasas']
        self.assertTrue(all(k.kind_id == self.kind_varenaya.pk for k in qs))
        self.assertEqual(qs.count(), 2)

    # TC-04
    def test_product_detail_correct_object(self):
        url = reverse('product_detail', args=[self.k1.pk])
        response = self.client.get(url)
        self.assertEqual(response.context['kolbasa'], self.k1)

    # TC-07
    def test_product_detail_404_if_not_exists(self):
        url = reverse('product_detail', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    # TC-08
    def test_product_list_empty(self):
        Kolbasa.objects.all().delete()
        url = reverse('product_list')
        response = self.client.get(url)
        self.assertEqual(len(response.context['kolbasas']), 0)

    # TC-10
    def test_product_list_context_keys(self):
        url = reverse('product_list')
        response = self.client.get(url)
        self.assertIn('kolbasas', response.context)
        self.assertIn('kinds', response.context)
        self.assertIn('current_sort', response.context)
    
    # TC‑11
    def test_kind_groups_page_lists_all_kinds(self):
        url = reverse('kind_groups')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/kind_groups.html')
        self.assertEqual(len(response.context['kinds']), 2)
        # Проверяем, что у каждого типа есть товары (предзагрузка)
        for kind in response.context['kinds']:
            self.assertTrue(hasattr(kind, 'kolbasas'))

    # TC‑12
    def test_kind_groups_shows_correct_counts(self):
        url = reverse('kind_groups')
        response = self.client.get(url)
        kind_names = [k.name for k in response.context['kinds']]
        self.assertIn('варёная', kind_names)
        self.assertIn('копчёная', kind_names)
        # Проверим, что у варёной 2 товара, у копчёной 1
        varenaya = next(k for k in response.context['kinds'] if k.name == 'варёная')
        kopch = next(k for k in response.context['kinds'] if k.name == 'копчёная')
        self.assertEqual(varenaya.kolbasas.count(), 2)
        self.assertEqual(kopch.kolbasas.count(), 1)