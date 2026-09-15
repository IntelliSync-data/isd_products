import base64
import json

from odoo.tests.common import HttpCase


class TestProductApi(HttpCase):

    ALLOWED_ORIGIN = 'https://allowed.example.com'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env['isd.product.category'].create({
            'name': 'API Test Category',
            'sort_order': 1,
        })
        # 1x1 transparent PNG
        test_image = base64.b64encode(
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
            b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01'
            b'\r\n\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        cls.product = cls.env['isd.product'].create({
            'name': 'API Test Image',
            'product_type': 'image',
            'category_ids': [(4, cls.category.id)],
            'product_file': test_image,
            'file_name': 'api_test.png',
        })

    def _put(self, product_id, payload, origin=None):
        headers = {'Content-Type': 'application/json'}
        if origin:
            headers['Origin'] = origin
        return self.opener.put(
            f'{self.base_url()}/api/v1/products/{product_id}',
            data=json.dumps(payload), headers=headers, timeout=12,
        )

    def _allow_origin(self):
        self.env['isd.product.allowed_origin'].create({'name': self.ALLOWED_ORIGIN})

    def test_get_categories(self):
        response = self.url_open('/api/v1/products/categories')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIsInstance(data['data'], list)
        self.assertIn('API Test Category', [c['name'] for c in data['data']])

    def test_get_products(self):
        response = self.url_open('/api/v1/products')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        for key in ('page', 'limit', 'total'):
            self.assertIn(key, data['meta'])

    def test_get_products_with_category_filter(self):
        response = self.url_open(f'/api/v1/products?categoryId={self.category.id}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn(self.product.id, [p['id'] for p in data['data']])

    def test_get_products_pagination(self):
        response = self.url_open('/api/v1/products?page=1&limit=5')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['meta']['page'], 1)
        self.assertEqual(data['meta']['limit'], 5)

    def test_get_version(self):
        response = self.url_open('/api/v1/products/version')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('version', data['data'])
        self.assertIn('last_updated', data['data'])

    def test_put_without_origin_is_rejected(self):
        self._allow_origin()
        response = self._put(self.product.id, {'name': 'Hacked'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.product.name, 'API Test Image')

    def test_put_rejected_when_no_origin_configured(self):
        response = self._put(self.product.id, {'name': 'Hacked'}, origin=self.ALLOWED_ORIGIN)
        self.assertEqual(response.status_code, 403)

    def test_put_with_wrong_origin_is_rejected(self):
        self._allow_origin()
        response = self._put(self.product.id, {'name': 'Hacked'}, origin='https://evil.example.com')
        self.assertEqual(response.status_code, 403)

    def test_put_with_allowed_origin_updates_product(self):
        self._allow_origin()
        response = self._put(
            self.product.id,
            {'description': 'Updated via API', 'note': 'Internal', 'is_visible': False},
            origin=self.ALLOWED_ORIGIN,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['description'], 'Updated via API')
        self.assertEqual(data['data']['note'], 'Internal')
        self.assertFalse(data['data']['is_visible'])

        listed_ids = [p['id'] for p in self.url_open('/api/v1/products').json()['data']]
        self.assertNotIn(self.product.id, listed_ids)

    def test_put_invalid_json(self):
        self._allow_origin()
        response = self.opener.put(
            f'{self.base_url()}/api/v1/products/{self.product.id}',
            data='not json', headers={'Content-Type': 'application/json', 'Origin': self.ALLOWED_ORIGIN},
            timeout=12,
        )
        self.assertEqual(response.status_code, 400)

    def test_put_unknown_field(self):
        self._allow_origin()
        response = self._put(self.product.id, {'product_type': 'video'}, origin=self.ALLOWED_ORIGIN)
        self.assertEqual(response.status_code, 400)

    def test_put_missing_product(self):
        self._allow_origin()
        response = self._put(999999, {'name': 'x'}, origin=self.ALLOWED_ORIGIN)
        self.assertEqual(response.status_code, 404)
