import hashlib
import logging
import os
import time

from odoo.tools import config

from .base import StorageProvider

_logger = logging.getLogger(__name__)


class LocalStorageProvider(StorageProvider):

    def _get_product_dir(self):
        data_dir = config.get('data_dir', '/var/lib/odoo')
        db_name = self.env.cr.dbname
        product_dir = os.path.join(data_dir, 'filestore', db_name, 'isd_products')
        os.makedirs(product_dir, exist_ok=True)
        return product_dir

    def _generate_key(self, file_name):
        timestamp = str(time.time()).encode()
        name_hash = hashlib.sha256(timestamp + file_name.encode()).hexdigest()[:16]
        ext = os.path.splitext(file_name)[1] or ''
        return f"product/{name_hash}{ext}"

    def upload(self, file_data, file_name, mime_type):
        storage_key = self._generate_key(file_name)
        product_dir = self._get_product_dir()
        file_path = os.path.join(product_dir, storage_key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'wb') as f:
            f.write(file_data)

        _logger.info("Local storage: uploaded %s (%d bytes)", storage_key, len(file_data))
        return storage_key

    def delete(self, storage_key):
        product_dir = self._get_product_dir()
        file_path = os.path.join(product_dir, storage_key)
        if os.path.exists(file_path):
            os.remove(file_path)
            _logger.info("Local storage: deleted %s", storage_key)

    def exists(self, storage_key):
        product_dir = self._get_product_dir()
        file_path = os.path.join(product_dir, storage_key)
        return os.path.exists(file_path)

    def get_url(self, storage_key):
        return f'/isd_products/file/{storage_key}'
