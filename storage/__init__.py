from .base import StorageProvider
from .local_storage import LocalStorageProvider
from .s3_storage import S3StorageProvider

_PROVIDERS = {
    'local': LocalStorageProvider,
    's3': S3StorageProvider,
}


def get_storage_provider(provider_type, env):
    provider_class = _PROVIDERS.get(provider_type)
    if not provider_class:
        raise ValueError(f"Unknown storage provider: {provider_type}")
    return provider_class(env)
