from markupsafe import Markup

from odoo import fields, models, api


class IsdProductApiDocWizard(models.TransientModel):
    _name = 'isd.product.api.doc.wizard'
    _description = 'Product API Documentation'

    documentation_html = fields.Html('Documentation')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'documentation_html' in fields_list:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
            res['documentation_html'] = Markup(self._generate_docs(base_url))
        return res

    @api.model
    def _generate_docs(self, base_url):
        return """
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 900px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px;">
                ISD Product Service - REST API Documentation
            </h1>
            <p style="color: #7f8c8d;">Base URL: <code style="background: #ecf0f1; padding: 2px 6px; border-radius: 3px;">%(base_url)s</code></p>

            <h2 style="color: #2c3e50; margin-top: 30px;">Response Format</h2>
            <pre style="background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 6px; overflow-x: auto;">{
    "success": true,
    "code": 200,
    "message": "",
    "meta": {},
    "data": []
}</pre>

            <hr style="margin: 30px 0; border: 1px solid #ecf0f1;"/>

            <h2 style="color: #2c3e50;">
                <span style="background: #27ae60; color: white; padding: 3px 10px; border-radius: 4px; font-size: 14px; margin-right: 10px;">GET</span>
                /api/v1/products/categories
            </h2>
            <p>Get all active categories sorted by sort_order.</p>

            <h4>Response</h4>
            <pre style="background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 6px; overflow-x: auto;">{
    "success": true,
    "code": 200,
    "message": "",
    "meta": {},
    "data": [
        {
            "id": 1,
            "name": "Electronics",
            "avatar": "/web/image/isd.product.category/1/avatar",
            "sort_order": 10
        }
    ]
}</pre>

            <h4>cURL Example</h4>
            <pre style="background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 6px; overflow-x: auto;">curl -X GET %(base_url)s/api/v1/products/categories</pre>

            <hr style="margin: 30px 0; border: 1px solid #ecf0f1;"/>

            <h2 style="color: #2c3e50;">
                <span style="background: #27ae60; color: white; padding: 3px 10px; border-radius: 4px; font-size: 14px; margin-right: 10px;">GET</span>
                /api/v1/products
            </h2>
            <p>Get paginated list of active, visible, published products. The internal <code>note</code> is never returned here.</p>

            <h4>Query Parameters</h4>
            <table style="width: 100%%; border-collapse: collapse; margin: 10px 0;">
                <thead>
                    <tr style="background: #ecf0f1;">
                        <th style="padding: 8px 12px; text-align: left; border: 1px solid #ddd;">Parameter</th>
                        <th style="padding: 8px 12px; text-align: left; border: 1px solid #ddd;">Type</th>
                        <th style="padding: 8px 12px; text-align: left; border: 1px solid #ddd;">Description</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding: 8px 12px; border: 1px solid #ddd;"><code>page</code></td>
                        <td style="padding: 8px 12px; border: 1px solid #ddd;">Integer</td>
                        <td style="padding: 8px 12px; border: 1px solid #ddd;">Page number (default: 1)</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 12px; border: 1px solid #ddd;"><code>limit</code></td>
                        <td style="padding: 8px 12px; border: 1px solid #ddd;">Integer</td>
                        <td style="padding: 8px 12px; border: 1px solid #ddd;">Items per page (default/max: API Maximum Return setting)</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 12px; border: 1px solid #ddd;"><code>categoryId</code></td>
                        <td style="padding: 8px 12px; border: 1px solid #ddd;">Integer</td>
                        <td style="padding: 8px 12px; border: 1px solid #ddd;">Filter by category ID</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 12px; border: 1px solid #ddd;"><code>include_hidden</code></td>
                        <td style="padding: 8px 12px; border: 1px solid #ddd;">1 / true</td>
                        <td style="padding: 8px 12px; border: 1px solid #ddd;">Also return hidden products (<code>is_visible: false</code>).
                            Requires an <code>Origin</code> header matching the Allowed Origins, like the PUT API, otherwise it returns <code>403</code>.</td>
                    </tr>
                </tbody>
            </table>

            <h4>Response</h4>
            <pre style="background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 6px; overflow-x: auto;">{
    "success": true,
    "code": 200,
    "message": "",
    "meta": {
        "page": 1,
        "limit": 20,
        "total": 58
    },
    "data": [
        {
            "id": 1,
            "name": "Product Name",
            "description": "Plain text description",
            "type": "image",
            "display_size": "medium",
            "is_visible": true,
            "categories": [{"id": 1, "name": "Electronics"}],
            "tags": [{"id": 1, "name": "featured"}],
            "url": "/isd_products/file/product/abc123.jpg",
            "thumbnail_url": "/isd_products/thumbnail/1?v=1757000000",
            "mime_type": "image/jpeg",
            "size": 245760,
            "created_at": "2026-09-01T10:30:00"
        }
    ]
}</pre>

            <h4>cURL Examples</h4>
            <pre style="background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 6px; overflow-x: auto;"># Get all products (default pagination)
curl -X GET %(base_url)s/api/v1/products

# Get page 2 with 10 items per page
curl -X GET "%(base_url)s/api/v1/products?page=2&amp;limit=10"

# Filter by category
curl -X GET "%(base_url)s/api/v1/products?categoryId=1"</pre>

            <hr style="margin: 30px 0; border: 1px solid #ecf0f1;"/>

            <h2 style="color: #2c3e50;">
                <span style="background: #e67e22; color: white; padding: 3px 10px; border-radius: 4px; font-size: 14px; margin-right: 10px;">PUT</span>
                /api/v1/products/{id}
            </h2>
            <p>Edit a product. Send only the fields you want to change.</p>

            <div style="background: #fdecea; border-left: 4px solid #e74c3c; padding: 12px 15px; margin: 10px 0;">
                <strong>Origin required.</strong> The request must send an <code>Origin</code> header matching one of the
                Allowed Origins in Settings, otherwise it returns <code>403</code>. If no Allowed Origins are configured,
                every PUT request is rejected. CORS is only enforced by browsers: server-side clients (curl, Postman, scripts)
                can set any <code>Origin</code> header.
            </div>

            <h4>Editable Fields</h4>
            <table style="width: 100%%; border-collapse: collapse; margin: 10px 0;">
                <thead>
                    <tr style="background: #ecf0f1;">
                        <th style="padding: 8px 12px; text-align: left; border: 1px solid #ddd;">Field</th>
                        <th style="padding: 8px 12px; text-align: left; border: 1px solid #ddd;">Type</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td style="padding: 8px 12px; border: 1px solid #ddd;"><code>name</code>, <code>description</code>, <code>note</code></td><td style="padding: 8px 12px; border: 1px solid #ddd;">String or null</td></tr>
                    <tr><td style="padding: 8px 12px; border: 1px solid #ddd;"><code>is_visible</code></td><td style="padding: 8px 12px; border: 1px solid #ddd;">Boolean</td></tr>
                    <tr><td style="padding: 8px 12px; border: 1px solid #ddd;"><code>sort_order</code></td><td style="padding: 8px 12px; border: 1px solid #ddd;">Integer</td></tr>
                    <tr><td style="padding: 8px 12px; border: 1px solid #ddd;"><code>display_size</code></td><td style="padding: 8px 12px; border: 1px solid #ddd;">small / medium / large</td></tr>
                    <tr><td style="padding: 8px 12px; border: 1px solid #ddd;"><code>category_ids</code></td><td style="padding: 8px 12px; border: 1px solid #ddd;">List of category IDs (cannot be empty)</td></tr>
                    <tr><td style="padding: 8px 12px; border: 1px solid #ddd;"><code>tag_ids</code></td><td style="padding: 8px 12px; border: 1px solid #ddd;">List of tag IDs</td></tr>
                    <tr><td style="padding: 8px 12px; border: 1px solid #ddd;"><code>publish_from</code>, <code>publish_to</code></td><td style="padding: 8px 12px; border: 1px solid #ddd;">ISO datetime (e.g. 2026-01-31T09:00:00Z) or null</td></tr>
                </tbody>
            </table>

            <h4>Response</h4>
            <p>The updated product, same shape as the list API plus the internal <code>note</code>.
            Unknown fields, wrong types or unknown IDs return <code>400</code>; a missing product returns <code>404</code>.</p>

            <h4>cURL Example</h4>
            <pre style="background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 6px; overflow-x: auto;">curl -X PUT %(base_url)s/api/v1/products/1 \\
  -H "Origin: https://your-site.com" \\
  -H "Content-Type: application/json" \\
  -d '{"description": "New description", "is_visible": false}'</pre>

            <hr style="margin: 30px 0; border: 1px solid #ecf0f1;"/>

            <h2 style="color: #2c3e50;">
                <span style="background: #27ae60; color: white; padding: 3px 10px; border-radius: 4px; font-size: 14px; margin-right: 10px;">GET</span>
                /api/v1/products/version
            </h2>
            <p>Get current data version for cache optimization. Version increments on any product or category change.</p>

            <h4>Response</h4>
            <pre style="background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 6px; overflow-x: auto;">{
    "success": true,
    "code": 200,
    "message": "",
    "meta": {},
    "data": {
        "version": 15,
        "last_updated": "2026-09-01T22:30:00"
    }
}</pre>

            <h4>cURL Example</h4>
            <pre style="background: #2d3436; color: #dfe6e9; padding: 15px; border-radius: 6px; overflow-x: auto;">curl -X GET %(base_url)s/api/v1/products/version</pre>

            <hr style="margin: 30px 0; border: 1px solid #ecf0f1;"/>

            <h2 style="color: #2c3e50;">Product Types</h2>
            <ul style="line-height: 2;">
                <li><strong>image</strong> - Uploaded image file (stored locally or on S3)</li>
                <li><strong>video</strong> - Uploaded video file (stored locally or on S3)</li>
                <li><strong>file</strong> - Uploaded document file (stored locally or on S3)</li>
                <li><strong>facebook</strong> - External Facebook URL (no file upload)</li>
                <li><strong>youtube</strong> - External YouTube URL (no file upload)</li>
            </ul>

            <h2 style="color: #2c3e50;">Business Rules</h2>
            <ul style="line-height: 2;">
                <li>The list API only returns <strong>active</strong> and <strong>visible</strong> products in active categories</li>
                <li>Products must be within their <strong>publish schedule</strong> to be returned</li>
                <li>Archived products are never returned; hidden products only with <code>include_hidden=1</code>, but both can still be edited via PUT</li>
                <li>If <code>limit</code> exceeds API Maximum Return, it is clamped to the maximum</li>
                <li>Read APIs check the origin only when an <code>Origin</code> header is sent and Allowed Origins are configured</li>
                <li>The PUT API always requires a matching <code>Origin</code> header</li>
            </ul>
        </div>
        """ % {'base_url': base_url}
