import base64
import logging
import os

from odoo import http
from odoo.http import request
from odoo.tools import config

_logger = logging.getLogger(__name__)


class IsdProductFileController(http.Controller):

    @http.route('/isd_products/thumbnail/<int:product_id>', type='http', auth='public', csrf=False)
    def serve_thumbnail(self, product_id, **kwargs):
        product = request.env['isd.product'].sudo().browse(product_id)
        if not product.exists() or not product.thumbnail:
            return request.not_found()

        image_data = base64.b64decode(product.thumbnail)
        headers = [
            ('Content-Type', 'image/jpeg'),
            ('Content-Length', str(len(image_data))),
            ('Cache-Control', 'public, max-age=31536000'),
        ]
        return request.make_response(image_data, headers=headers)

    @http.route('/isd_products/file/<path:storage_key>', type='http', auth='public', csrf=False)
    def serve_file(self, storage_key, **kwargs):
        data_dir = config.get('data_dir', '/var/lib/odoo')
        db_name = request.env.cr.dbname
        product_dir = os.path.join(data_dir, 'filestore', db_name, 'isd_products')
        file_path = os.path.join(product_dir, storage_key)

        real_product_dir = os.path.realpath(product_dir)
        real_file_path = os.path.realpath(file_path)
        if not real_file_path.startswith(real_product_dir):
            return request.not_found()

        if not os.path.exists(file_path):
            return request.not_found()

        import mimetypes
        mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'

        with open(file_path, 'rb') as f:
            file_data = f.read()

        headers = [
            ('Content-Type', mime_type),
            ('Content-Length', str(len(file_data))),
            ('Cache-Control', 'public, max-age=31536000'),
        ]

        if kwargs.get('download'):
            filename = os.path.basename(file_path)
            headers.append(('Content-Disposition', f'attachment; filename="{filename}"'))

        return request.make_response(file_data, headers=headers)
