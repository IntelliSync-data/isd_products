from odoo import fields, models


class IsdProductAllowedOrigin(models.Model):
    _name = 'isd.product.allowed_origin'
    _description = 'Product Allowed Origin'
    _order = 'id asc'

    name = fields.Char('Origin URL', required=True, help='e.g. https://portal.company.com')
    active = fields.Boolean('Active', default=True)
