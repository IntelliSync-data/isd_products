from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    isd_products_total_images = fields.Integer('Total Images', readonly=True)
    isd_products_total_videos = fields.Integer('Total Videos/URLs', readonly=True)
    isd_products_total_files = fields.Integer('Total Files', readonly=True)
    isd_products_total_categories = fields.Integer('Total Categories', readonly=True)

    isd_products_max_image_count = fields.Integer('Maximum Image Count')
    isd_products_max_video_count = fields.Integer('Maximum Video Count')
    isd_products_max_file_count = fields.Integer('Maximum File Count')
    isd_products_max_image_upload_size = fields.Float('Maximum Image Upload Size (MB)', default=10.0)
    isd_products_max_video_upload_size = fields.Float('Maximum Video Upload Size (MB)', default=100.0)
    isd_products_max_file_upload_size = fields.Float('Maximum File Upload Size (MB)', default=50.0)

    isd_products_api_max_return = fields.Integer('API Maximum Return', default=100)

    isd_products_storage_provider = fields.Selection([
        ('local', 'Local Storage'),
        ('s3', 'Amazon S3'),
    ], string='Storage Provider', default='local')

    isd_products_s3_bucket_name = fields.Char('Bucket Name')
    isd_products_s3_region = fields.Char('Region')
    isd_products_s3_access_key = fields.Char('Access Key')
    isd_products_s3_secret_key = fields.Char('Secret Key')
    isd_products_s3_endpoint_url = fields.Char('Endpoint URL')
    isd_products_s3_public_base_url = fields.Char('Public Base URL')
    isd_products_s3_use_ssl = fields.Boolean('Use SSL', default=True)

    isd_products_allowed_origin_ids = fields.Many2many(
        'isd.product.allowed_origin', string='Allowed Origins',
        compute='_compute_allowed_origins', inverse='_inverse_allowed_origins')

    def _compute_allowed_origins(self):
        origins = self.env['isd.product.allowed_origin'].sudo().search([])
        for record in self:
            record.isd_products_allowed_origin_ids = origins

    def _inverse_allowed_origins(self):
        pass

    @api.model
    def get_values(self):
        res = super().get_values()
        ICP = self.env['ir.config_parameter'].sudo()
        Product = self.env['isd.product'].sudo()
        Category = self.env['isd.product.category'].sudo()
        res.update(
            isd_products_total_images=Product.search_count([('product_type', '=', 'image'), ('active', '=', True)]),
            isd_products_total_videos=Product.search_count([
                ('product_type', 'in', ('video', 'facebook', 'youtube')),
                ('active', '=', True),
            ]),
            isd_products_total_files=Product.search_count([('product_type', '=', 'file'), ('active', '=', True)]),
            isd_products_total_categories=Category.search_count([('active', '=', True)]),
            isd_products_max_image_count=int(ICP.get_param('isd_products.max_image_count', '0')),
            isd_products_max_video_count=int(ICP.get_param('isd_products.max_video_count', '0')),
            isd_products_max_file_count=int(ICP.get_param('isd_products.max_file_count', '0')),
            isd_products_max_image_upload_size=float(ICP.get_param('isd_products.max_image_upload_size', '10')),
            isd_products_max_video_upload_size=float(ICP.get_param('isd_products.max_video_upload_size', '100')),
            isd_products_max_file_upload_size=float(ICP.get_param('isd_products.max_file_upload_size', '50')),
            isd_products_api_max_return=int(ICP.get_param('isd_products.api_max_return', '100')),
            isd_products_storage_provider=ICP.get_param('isd_products.storage_provider', 'local'),
            isd_products_s3_bucket_name=ICP.get_param('isd_products.s3_bucket_name', ''),
            isd_products_s3_region=ICP.get_param('isd_products.s3_region', ''),
            isd_products_s3_access_key=ICP.get_param('isd_products.s3_access_key', ''),
            isd_products_s3_secret_key=ICP.get_param('isd_products.s3_secret_key', ''),
            isd_products_s3_endpoint_url=ICP.get_param('isd_products.s3_endpoint_url', ''),
            isd_products_s3_public_base_url=ICP.get_param('isd_products.s3_public_base_url', ''),
            isd_products_s3_use_ssl=ICP.get_param('isd_products.s3_use_ssl', 'True') == 'True',
        )
        return res

    def set_values(self):
        super().set_values()
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('isd_products.max_image_count', str(self.isd_products_max_image_count))
        ICP.set_param('isd_products.max_video_count', str(self.isd_products_max_video_count))
        ICP.set_param('isd_products.max_file_count', str(self.isd_products_max_file_count))
        ICP.set_param('isd_products.max_image_upload_size', str(self.isd_products_max_image_upload_size))
        ICP.set_param('isd_products.max_video_upload_size', str(self.isd_products_max_video_upload_size))
        ICP.set_param('isd_products.max_file_upload_size', str(self.isd_products_max_file_upload_size))
        ICP.set_param('isd_products.api_max_return', str(self.isd_products_api_max_return))
        ICP.set_param('isd_products.storage_provider', self.isd_products_storage_provider)
        ICP.set_param('isd_products.s3_bucket_name', self.isd_products_s3_bucket_name or '')
        ICP.set_param('isd_products.s3_region', self.isd_products_s3_region or '')
        ICP.set_param('isd_products.s3_access_key', self.isd_products_s3_access_key or '')
        ICP.set_param('isd_products.s3_secret_key', self.isd_products_s3_secret_key or '')
        ICP.set_param('isd_products.s3_endpoint_url', self.isd_products_s3_endpoint_url or '')
        ICP.set_param('isd_products.s3_public_base_url', self.isd_products_s3_public_base_url or '')
        ICP.set_param('isd_products.s3_use_ssl', str(self.isd_products_s3_use_ssl))

    def action_view_api_documentation(self):
        return {
            'name': 'API Documentation',
            'type': 'ir.actions.act_window',
            'res_model': 'isd.product.api.doc.wizard',
            'view_mode': 'form',
            'target': 'new',
        }
