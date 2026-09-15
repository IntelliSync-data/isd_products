from odoo import fields, models, api


class IsdProductCategory(models.Model):
    _name = 'isd.product.category'
    _description = 'Product Category'
    _order = 'sort_order asc, id desc'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    avatar = fields.Image('Avatar', max_width=256, max_height=256)
    sort_order = fields.Integer('Sort Order', default=10)
    active = fields.Boolean('Active', default=True)

    product_ids = fields.Many2many('isd.product', string='Products')
    product_count = fields.Integer('Product Count', compute='_compute_product_count')

    @api.depends('product_ids')
    def _compute_product_count(self):
        for record in self:
            record.product_count = len(record.product_ids)

    def write(self, vals):
        res = super().write(vals)
        self._increment_version()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        self._increment_version()
        return records

    def _increment_version(self):
        ICP = self.env['ir.config_parameter'].sudo()
        current = int(ICP.get_param('isd_products.api_version', '0'))
        ICP.set_param('isd_products.api_version', str(current + 1))
        ICP.set_param('isd_products.api_last_updated', fields.Datetime.now())
