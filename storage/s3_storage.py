import hashlib
import logging
import time
import os

from .base import StorageProvider

_logger = logging.getLogger(__name__)


class S3StorageProvider(StorageProvider):

    def _get_client(self):
        import boto3
        endpoint_url = self.ICP.get_param('isd_products.s3_endpoint_url', '')
        use_ssl = self.ICP.get_param('isd_products.s3_use_ssl', 'True') == 'True'

        kwargs = {
            'aws_access_key_id': self.ICP.get_param('isd_products.s3_access_key', ''),
            'aws_secret_access_key': self.ICP.get_param('isd_products.s3_secret_key', ''),
            'region_name': self.ICP.get_param('isd_products.s3_region', ''),
            'use_ssl': use_ssl,
        }
        if endpoint_url:
            kwargs['endpoint_url'] = endpoint_url

        return boto3.client('s3', **kwargs)

    def _get_bucket(self):
        return self.ICP.get_param('isd_products.s3_bucket_name', '')

    def _generate_key(self, file_name):
        timestamp = str(time.time()).encode()
        name_hash = hashlib.sha256(timestamp + file_name.encode()).hexdigest()[:16]
        ext = os.path.splitext(file_name)[1] or ''
        return f"product/{name_hash}{ext}"

    def upload(self, file_data, file_name, mime_type):
        client = self._get_client()
        bucket = self._get_bucket()
        storage_key = self._generate_key(file_name)

        client.put_object(
            Bucket=bucket,
            Key=storage_key,
            Body=file_data,
            ContentType=mime_type,
        )
        _logger.info("S3 storage: uploaded %s to %s (%d bytes)", storage_key, bucket, len(file_data))
        return storage_key

    def delete(self, storage_key):
        client = self._get_client()
        bucket = self._get_bucket()
        client.delete_object(Bucket=bucket, Key=storage_key)
        _logger.info("S3 storage: deleted %s from %s", storage_key, bucket)

    def exists(self, storage_key):
        client = self._get_client()
        bucket = self._get_bucket()
        try:
            client.head_object(Bucket=bucket, Key=storage_key)
            return True
        except client.exceptions.ClientError:
            return False

    def get_url(self, storage_key):
        public_base_url = self.ICP.get_param('isd_products.s3_public_base_url', '')
        if public_base_url:
            return f"{public_base_url.rstrip('/')}/{storage_key}"

        bucket = self._get_bucket()
        region = self.ICP.get_param('isd_products.s3_region', '')
        endpoint_url = self.ICP.get_param('isd_products.s3_endpoint_url', '')

        if endpoint_url:
            return f"{endpoint_url.rstrip('/')}/{bucket}/{storage_key}"

        return f"https://{bucket}.s3.{region}.amazonaws.com/{storage_key}"
