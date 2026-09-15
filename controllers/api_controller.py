import json
import logging

from odoo import http
from odoo.http import request

from ..services.product_service import ProductApiError, ProductService
from ..services.category_service import CategoryService

_logger = logging.getLogger(__name__)


class IsdProductApiController(http.Controller):

    def _check_origin(self, strict=False):
        """Validate the Origin header against the configured Allowed Origins.

        Non-strict (read APIs): requests without an Origin header, or when no
        origins are configured, are allowed.
        Strict (write APIs): an Origin header matching a configured origin is required.
        """
        origin = request.httprequest.headers.get('Origin', '')
        allowed = request.env['isd.product.allowed_origin'].sudo().search([
            ('active', '=', True),
        ])
        allowed_urls = [o.name.rstrip('/') for o in allowed]

        if strict:
            if not origin or not allowed_urls or origin.rstrip('/') not in allowed_urls:
                return self._error_response(403, 'Origin not allowed')
            return None

        if not origin or not allowed_urls:
            return None
        if origin.rstrip('/') not in allowed_urls:
            return self._error_response(403, 'Origin not allowed')
        return None

    def _success_response(self, data=None, meta=None, code=200, message=''):
        body = {
            'success': True,
            'code': code,
            'message': message,
            'meta': meta or {},
            'data': data if data is not None else [],
        }
        headers = self._cors_headers()
        return request.make_response(
            json.dumps(body, default=str),
            headers=[('Content-Type', 'application/json')] + headers,
            status=code,
        )

    def _error_response(self, code, message):
        body = {
            'success': False,
            'code': code,
            'message': message,
            'meta': {},
            'data': [],
        }
        headers = self._cors_headers()
        return request.make_response(
            json.dumps(body, default=str),
            headers=[('Content-Type', 'application/json')] + headers,
            status=code,
        )

    def _cors_headers(self):
        origin = request.httprequest.headers.get('Origin', '')
        headers = [
            ('Access-Control-Allow-Methods', 'GET, PUT, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type, Authorization'),
            ('Access-Control-Max-Age', '3600'),
        ]
        if origin:
            headers.append(('Access-Control-Allow-Origin', origin))
        return headers

    @http.route([
        '/api/v1/products/categories',
        '/api/v1/products',
        '/api/v1/products/version',
        '/api/v1/products/<int:product_id>',
    ], type='http', auth='public', methods=['OPTIONS'], csrf=False)
    def options_handler(self, **kwargs):
        headers = self._cors_headers()
        return request.make_response('', headers=headers, status=204)

    @http.route('/api/v1/products/categories', type='http', auth='public', methods=['GET'], csrf=False)
    def get_categories(self, **kwargs):
        origin_error = self._check_origin()
        if origin_error:
            return origin_error

        try:
            service = CategoryService(request.env)
            items = service.get_categories()
            return self._success_response(data=items)
        except Exception as e:
            _logger.exception("Error in GET /api/v1/products/categories")
            return self._error_response(500, str(e))

    @http.route('/api/v1/products', type='http', auth='public', methods=['GET'], csrf=False)
    def get_products(self, **kwargs):
        origin_error = self._check_origin()
        if origin_error:
            return origin_error

        try:
            page = int(kwargs.get('page', 1))
            limit = int(kwargs.get('limit', 0)) or None
            category_id = int(kwargs.get('categoryId', 0)) or None

            service = ProductService(request.env)
            result = service.get_product_list(page=page, limit=limit, category_id=category_id)

            meta = {
                'page': result['page'],
                'limit': result['limit'],
                'total': result['total'],
            }
            return self._success_response(data=result['items'], meta=meta)
        except Exception as e:
            _logger.exception("Error in GET /api/v1/products")
            return self._error_response(500, str(e))

    @http.route('/api/v1/products/version', type='http', auth='public', methods=['GET'], csrf=False)
    def get_version(self, **kwargs):
        origin_error = self._check_origin()
        if origin_error:
            return origin_error

        try:
            service = ProductService(request.env)
            result = service.get_version()
            return self._success_response(data=result)
        except Exception as e:
            _logger.exception("Error in GET /api/v1/products/version")
            return self._error_response(500, str(e))

    @http.route('/api/v1/products/<int:product_id>', type='http', auth='public', methods=['PUT'], csrf=False)
    def update_product(self, product_id, **kwargs):
        origin_error = self._check_origin(strict=True)
        if origin_error:
            return origin_error

        raw_body = request.httprequest.get_data(as_text=True)
        try:
            payload = json.loads(raw_body) if raw_body else None
        except ValueError:
            return self._error_response(400, 'Request body must be valid JSON')

        try:
            service = ProductService(request.env)
            result = service.update_product(product_id, payload)
            return self._success_response(data=result)
        except ProductApiError as e:
            return self._error_response(e.code, e.message)
        except Exception as e:
            _logger.exception("Error in PUT /api/v1/products/%s", product_id)
            return self._error_response(500, str(e))
