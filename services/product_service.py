from datetime import datetime, timezone

from odoo import fields
from odoo.exceptions import ValidationError


class ProductApiError(Exception):

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


class ProductService:

    EDITABLE_FIELDS = (
        'name', 'description', 'note', 'is_visible', 'sort_order', 'display_size',
        'category_ids', 'tag_ids', 'publish_from', 'publish_to',
    )

    def __init__(self, env):
        self.env = env
        self.ICP = env['ir.config_parameter'].sudo()

    def get_product_list(self, page=1, limit=None, category_id=None):
        max_return = int(self.ICP.get_param('isd_products.api_max_return', '100'))

        if not limit or limit <= 0:
            limit = max_return
        if limit > max_return:
            limit = max_return
        if page < 1:
            page = 1

        domain = [('active', '=', True), ('is_visible', '=', True), ('is_published', '=', True)]
        domain.append(('category_ids.active', '=', True))

        if category_id:
            domain.append(('category_ids', 'in', [category_id]))

        Product = self.env['isd.product'].sudo()
        total = Product.search_count(domain)
        offset = (page - 1) * limit
        records = Product.search(domain, limit=limit, offset=offset, order='sort_order asc, id desc')

        items = []
        for rec in records:
            items.append(self._serialize_product(rec))

        return {
            'items': items,
            'page': page,
            'limit': limit,
            'total': total,
        }

    def get_version(self):
        version = int(self.ICP.get_param('isd_products.api_version', '0'))
        last_updated = self.ICP.get_param('isd_products.api_last_updated', '')
        return {
            'version': version,
            'last_updated': last_updated or None,
        }

    def update_product(self, product_id, payload):
        if not isinstance(payload, dict) or not payload:
            raise ProductApiError(400, 'Request body must be a non-empty JSON object')

        unknown = sorted(set(payload) - set(self.EDITABLE_FIELDS))
        if unknown:
            raise ProductApiError(
                400, 'Unsupported fields: %s. Editable fields: %s' % (
                    ', '.join(unknown), ', '.join(self.EDITABLE_FIELDS)))

        product = self.env['isd.product'].sudo().with_context(active_test=False).browse(product_id).exists()
        if not product:
            raise ProductApiError(404, 'Product not found')

        vals = {}
        for key, value in payload.items():
            vals[key] = self._parse_field(key, value)

        try:
            product.write(vals)
        except ValidationError as e:
            raise ProductApiError(400, str(e))

        result = self._serialize_product(product)
        result['note'] = product.note or ''
        return result

    def _parse_field(self, key, value):
        if key in ('name', 'description', 'note'):
            if value is not None and not isinstance(value, str):
                raise ProductApiError(400, "'%s' must be a string or null" % key)
            return value or False

        if key == 'is_visible':
            if not isinstance(value, bool):
                raise ProductApiError(400, "'is_visible' must be true or false")
            return value

        if key == 'sort_order':
            if isinstance(value, bool) or not isinstance(value, int):
                raise ProductApiError(400, "'sort_order' must be an integer")
            return value

        if key == 'display_size':
            allowed = [option[0] for option in self.env['isd.product']._fields['display_size'].selection]
            if value not in allowed:
                raise ProductApiError(400, "'display_size' must be one of: %s" % ', '.join(allowed))
            return value

        if key in ('category_ids', 'tag_ids'):
            model = 'isd.product.category' if key == 'category_ids' else 'isd.product.tag'
            if not isinstance(value, list) or any(isinstance(i, bool) or not isinstance(i, int) for i in value):
                raise ProductApiError(400, "'%s' must be a list of integer ids" % key)
            if key == 'category_ids' and not value:
                raise ProductApiError(400, "'category_ids' cannot be empty")
            existing = self.env[model].sudo().with_context(active_test=False).browse(value).exists()
            missing = sorted(set(value) - set(existing.ids))
            if missing:
                raise ProductApiError(400, "'%s' contains unknown ids: %s" % (key, ', '.join(map(str, missing))))
            return [(6, 0, value)]

        if key in ('publish_from', 'publish_to'):
            if value is None:
                return False
            if not isinstance(value, str):
                raise ProductApiError(400, "'%s' must be an ISO datetime string or null" % key)
            try:
                parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                raise ProductApiError(400, "'%s' must be an ISO datetime string, e.g. 2026-01-31T09:00:00Z" % key)
            if parsed.tzinfo:
                parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
            return fields.Datetime.to_string(parsed)

        raise ProductApiError(400, "Unsupported field: %s" % key)

    def _serialize_product(self, record):
        categories = []
        for cat in record.category_ids.filtered('active'):
            categories.append({
                'id': cat.id,
                'name': cat.name,
            })

        tags = []
        for tag in record.tag_ids.filtered('active'):
            tags.append({
                'id': tag.id,
                'name': tag.name,
            })

        result = {
            'id': record.id,
            'name': record.name or '',
            'description': record.description or '',
            'type': record.product_type,
            'display_size': record.display_size or 'medium',
            'is_visible': record.is_visible,
            'categories': categories,
            'tags': tags,
            'url': record.public_url or '',
            'thumbnail_url': record.thumbnail_url or '',
            'mime_type': record.mime_type or '',
            'size': record.file_size,
            'created_at': record.create_date.isoformat() if record.create_date else None,
        }

        if record.product_type in ('facebook', 'youtube'):
            result['external_url'] = record.external_url or ''

        return result
