import abc


class StorageProvider(abc.ABC):

    def __init__(self, env):
        self.env = env
        self.ICP = env['ir.config_parameter'].sudo()

    @abc.abstractmethod
    def upload(self, file_data, file_name, mime_type):
        pass

    @abc.abstractmethod
    def delete(self, storage_key):
        pass

    @abc.abstractmethod
    def exists(self, storage_key):
        pass

    @abc.abstractmethod
    def get_url(self, storage_key):
        pass
