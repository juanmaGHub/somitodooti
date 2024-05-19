from odoo import models, fields, api, _


class ProductCategory(models.Model):
    _inherit = "product.category"

    code = fields.Char('Code', index=True)