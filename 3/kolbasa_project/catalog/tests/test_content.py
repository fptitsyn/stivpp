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
            weight=300, precut=False
        )
        cls.k2 = Kolbasa.objects.create(
            article='C002', brand='Бета', kind=cls.kind_kopch,
            weight=1200, precut=True, num_of_slices=12
        )
        cls.k3 = Kolbasa.objects.create(
            article='C003', brand='Гамма', kind=cls.kind_varenaya,
            weight=150, precut=True, num_of_slices=5
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

    def test_product_list_empty(self):
        Kolbasa.objects.all().delete()
        url = reverse('product_list')
        response = self.client.get(url)
        self.assertEqual(len(response.context['kolbasas']), 0)

    def test_product_list_filter_by_kind(self):
        url = reverse('product_list') + f'?kind={self.kind_varenaya.pk}'
        response = self.client.get(url)
        qs = response.context['kolbasas']
        self.assertTrue(all(k.kind_id == self.kind_varenaya.pk for k in qs))
        self.assertEqual(qs.count(), 2)

    def test_product_list_sort_by_brand(self):
        url = reverse('product_list') + '?sort=brand'
        response = self.client.get(url)
        brands = [k.brand for k in response.context['kolbasas']]
        self.assertEqual(brands, ['Альфа', 'Бета', 'Гамма'])  # алфавитный порядок

    def test_product_list_sort_by_weight(self):
        url = reverse('product_list') + '?sort=weight'
        response = self.client.get(url)
        weights = [k.weight for k in response.context['kolbasas']]
        self.assertEqual(weights, [150, 300, 1200])

    def test_product_list_sort_by_kind(self):
        url = reverse('product_list') + '?sort=kind'
        response = self.client.get(url)
        kinds = [k.kind.name for k in response.context['kolbasas']]
        # Ожидаем: варёная, варёная, копчёная
        self.assertEqual(kinds, ['варёная', 'варёная', 'копчёная'])

    def test_product_list_sort_by_num_slices(self):
        url = reverse('product_list') + '?sort=num_slices'
        response = self.client.get(url)
        slices = [k.num_of_slices for k in response.context['kolbasas']]
        # None (k1) будет в начале или конце? в SQLite None идёт первым при сортировке ASC
        self.assertEqual(slices, [None, 5, 12])  # стандартное поведение Django

    def test_product_detail_correct_object(self):
        url = reverse('product_detail', args=[self.k1.pk])
        response = self.client.get(url)
        self.assertEqual(response.context['kolbasa'], self.k1)

    def test_product_detail_404_if_not_exists(self):
        url = reverse('product_detail', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_about_page_contains_text(self):
        url = reverse('about')
        response = self.client.get(url)
        self.assertContains(response, 'О нашем сервисе')

    def test_product_list_context_keys(self):
        url = reverse('product_list')
        response = self.client.get(url)
        self.assertIn('kolbasas', response.context)
        self.assertIn('kinds', response.context)
        self.assertIn('current_sort', response.context)