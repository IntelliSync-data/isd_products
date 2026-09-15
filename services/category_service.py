class CategoryService:

    def __init__(self, env):
        self.env = env

    def get_categories(self):
        Category = self.env['isd.product.category'].sudo()
        records = Category.search(
            [('active', '=', True)],
            order='sort_order asc',
        )

        items = []
        for rec in records:
            avatar_url = f'/web/image/isd.product.category/{rec.id}/avatar' if rec.avatar else ''
            items.append({
                'id': rec.id,
                'name': rec.name,
                'avatar': avatar_url,
                'sort_order': rec.sort_order,
            })

        return items
