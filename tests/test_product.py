import base64
from datetime import datetime, timedelta

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

from ..services.product_service import ProductApiError, ProductService


class ProductTestBase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env['isd.product.category'].create({
            'name': 'Test Category',
            'sort_order': 1,
        })
        cls.tag = cls.env['isd.product.tag'].create({
            'name': 'test-tag',
        })
        # 1x1 transparent PNG
        cls.test_image_data = base64.b64encode(
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
            b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01'
            b'\r\n\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        )

    def _create_image(self, **extra):
        vals = {
            'name': 'Test Image',
            'product_type': 'image',
            'category_ids': [(4, self.category.id)],
            'product_file': self.test_image_data,
            'file_name': 'test.png',
        }
        vals.update(extra)
        return self.env['isd.product'].create(vals)


class TestIsdProduct(ProductTestBase):

    def test_create_product(self):
        product = self._create_image()
        self.assertTrue(product.id)
        self.assertEqual(product.product_type, 'image')
        self.assertTrue(product.storage_key)
        self.assertEqual(product.storage_provider, 'local')
        self.assertTrue(product.file_size > 0)
        self.assertEqual(product.mime_type, 'image/png')
        self.assertTrue(product.is_visible)

    def test_create_product_without_file_fails(self):
        with self.assertRaises(ValidationError):
            self.env['isd.product'].create({
                'name': 'No File',
                'product_type': 'image',
                'category_ids': [(4, self.category.id)],
            })

    def test_file_size_limit(self):
        self.env['ir.config_parameter'].sudo().set_param('isd_products.max_image_upload_size', '0.00001')
        with self.assertRaises(ValidationError):
            self._create_image(name='Too Large', file_name='big.png')

    def test_publish_schedule_always(self):
        self.assertTrue(self._create_image(name='Always Published').is_published)

    def test_publish_schedule_future(self):
        product = self._create_image(name='Future', publish_from=datetime.now() + timedelta(days=1))
        self.assertFalse(product.is_published)

    def test_publish_schedule_past(self):
        product = self._create_image(name='Past', publish_to=datetime.now() - timedelta(days=1))
        self.assertFalse(product.is_published)

    def test_category_version_increment(self):
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('isd_products.api_version', '0')
        self.env['isd.product.category'].create({'name': 'V Test'})
        self.assertGreater(int(ICP.get_param('isd_products.api_version', '0')), 0)

    def test_product_version_increment(self):
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('isd_products.api_version', '0')
        self._create_image(name='V Test')
        self.assertGreater(int(ICP.get_param('isd_products.api_version', '0')), 0)

    def test_file_size_display(self):
        self.assertTrue(self._create_image(name='Size Test').file_size_display)

    def test_thumbnail_url_is_versioned(self):
        product = self.env['isd.product'].create({
            'name': 'Video With Thumbnail',
            'product_type': 'video',
            'category_ids': [(4, self.category.id)],
            'product_file': self.test_image_data,
            'file_name': 'test.mp4',
            'thumbnail': self.test_image_data,
        })
        self.assertTrue(product.thumbnail_url.startswith(f'/isd_products/thumbnail/{product.id}?v='))


class TestProductService(ProductTestBase):

    def test_hidden_product_excluded_from_list(self):
        visible = self._create_image(name='Visible')
        hidden = self._create_image(name='Hidden', is_visible=False)
        ids = [item['id'] for item in ProductService(self.env).get_product_list()['items']]
        self.assertIn(visible.id, ids)
        self.assertNotIn(hidden.id, ids)

    def test_list_returns_description_but_not_note(self):
        product = self._create_image(description='Public text', note='Internal text')
        item = next(i for i in ProductService(self.env).get_product_list()['items'] if i['id'] == product.id)
        self.assertEqual(item['description'], 'Public text')
        self.assertNotIn('note', item)

    def test_update_product_fields(self):
        product = self._create_image()
        result = ProductService(self.env).update_product(product.id, {
            'name': 'Renamed',
            'description': 'New description',
            'note': 'New note',
            'is_visible': False,
            'sort_order': 3,
            'display_size': 'large',
            'tag_ids': [self.tag.id],
            'publish_from': '2026-01-31T09:00:00Z',
        })
        self.assertEqual(product.name, 'Renamed')
        self.assertEqual(product.description, 'New description')
        self.assertEqual(product.note, 'New note')
        self.assertFalse(product.is_visible)
        self.assertEqual(product.sort_order, 3)
        self.assertEqual(product.display_size, 'large')
        self.assertEqual(product.tag_ids, self.tag)
        self.assertEqual(product.publish_from, datetime(2026, 1, 31, 9, 0, 0))
        self.assertEqual(result['note'], 'New note')
        self.assertFalse(result['is_visible'])

    def test_update_rejects_unknown_field(self):
        product = self._create_image()
        with self.assertRaises(ProductApiError) as ctx:
            ProductService(self.env).update_product(product.id, {'product_file': 'x'})
        self.assertEqual(ctx.exception.code, 400)

    def test_update_rejects_wrong_type(self):
        product = self._create_image()
        with self.assertRaises(ProductApiError) as ctx:
            ProductService(self.env).update_product(product.id, {'is_visible': 'no'})
        self.assertEqual(ctx.exception.code, 400)

    def test_update_rejects_empty_categories(self):
        product = self._create_image()
        with self.assertRaises(ProductApiError) as ctx:
            ProductService(self.env).update_product(product.id, {'category_ids': []})
        self.assertEqual(ctx.exception.code, 400)

    def test_update_rejects_unknown_ids(self):
        product = self._create_image()
        with self.assertRaises(ProductApiError) as ctx:
            ProductService(self.env).update_product(product.id, {'tag_ids': [999999]})
        self.assertEqual(ctx.exception.code, 400)

    def test_update_missing_product(self):
        with self.assertRaises(ProductApiError) as ctx:
            ProductService(self.env).update_product(999999, {'name': 'x'})
        self.assertEqual(ctx.exception.code, 404)
