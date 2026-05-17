from django.test import TestCase
from django.urls import reverse
from catalog.models import Kind, Kolbasa

class RouteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.kind = Kind.objects.create(name='варёная')
        cls.kolbasa = Kolbasa.objects.create(
            article='RT001', brand='Тест', kind=cls.kind, weight=500
        )

    # TC-01
    def test_product_list_url_resolves(self):
        url = reverse('product_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_product_detail_url_resolves(self):
        url = reverse('product_detail', args=[self.kolbasa.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    # TC-05
    def test_product_detail_nonexistent_returns_404(self):
        url = reverse('product_detail', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    # TC-06
    def test_about_url_resolves(self):
        url = reverse('about')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    # TC-09
    def test_reverse_product_list_matches_root(self):
        self.assertEqual(reverse('product_list'), '/')

    def test_reverse_product_detail_matches_expected(self):
        self.assertEqual(
            reverse('product_detail', args=[self.kolbasa.pk]),
            f'/product/{self.kolbasa.pk}/'
        )

    def test_reverse_about_matches_expected(self):
        self.assertEqual(reverse('about'), '/about/')