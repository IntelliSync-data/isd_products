from odoo.tests.common import TransactionCase


class TestLocalStorage(TransactionCase):

    def test_upload_and_get_url(self):
        from ..storage.local_storage import LocalStorageProvider
        provider = LocalStorageProvider(self.env)

        storage_key = provider.upload(b'test file content', 'test.txt', 'text/plain')

        self.assertTrue(storage_key)
        self.assertTrue(storage_key.startswith('product/'))
        self.assertTrue(provider.exists(storage_key))
        self.assertTrue(provider.get_url(storage_key).startswith('/isd_products/file/'))

        provider.delete(storage_key)
        self.assertFalse(provider.exists(storage_key))

    def test_delete_nonexistent(self):
        from ..storage.local_storage import LocalStorageProvider
        LocalStorageProvider(self.env).delete('product/nonexistent.txt')


class TestS3Storage(TransactionCase):

    def test_get_url_with_public_base(self):
        from ..storage.s3_storage import S3StorageProvider
        self.env['ir.config_parameter'].sudo().set_param('isd_products.s3_public_base_url', 'https://cdn.example.com')

        url = S3StorageProvider(self.env).get_url('product/test.jpg')
        self.assertEqual(url, 'https://cdn.example.com/product/test.jpg')

    def test_get_url_without_public_base(self):
        from ..storage.s3_storage import S3StorageProvider
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('isd_products.s3_public_base_url', '')
        ICP.set_param('isd_products.s3_bucket_name', 'my-bucket')
        ICP.set_param('isd_products.s3_region', 'ap-southeast-1')
        ICP.set_param('isd_products.s3_endpoint_url', '')

        url = S3StorageProvider(self.env).get_url('product/test.jpg')
        self.assertEqual(url, 'https://my-bucket.s3.ap-southeast-1.amazonaws.com/product/test.jpg')
