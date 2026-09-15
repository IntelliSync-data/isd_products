from odoo import fields, models


class IsdProductTag(models.Model):
    _name = 'isd.product.tag'
    _description = 'Product Tag'
    _order = 'name asc'

    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True)
