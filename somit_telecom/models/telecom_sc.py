from ..commons.utils import parse_dates
from odoo import models, fields, api, _


class TelecomServiceConsumption(models.Model):
    _name = 'telecom.service.consumption'
    _description = 'Telecom Service Management Model'
    _order = 'consumption_timestamp desc'

    def _get_domain_product_tmpl_id(self):
        return [
            '&',
                ('categ_id.parent_id', '=', self.env.ref('somit_telecom.product_category_telecom').id),
                '|', ('company_id', '=', False), ('company_id', '=', self.env.company.id)
        ]
    
    name = fields.Char('Name', compute='_compute_name', store=True, default=_('New'), index=True, readonly=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company, index=True, required=True)
    
    # Telecom Service Product
    product_tmpl_id = fields.Many2one(
        'product.template',
        'Telecom Service Template',
        required=True,
        ondelete='cascade',
        index=True,
        check_company=True,
        domain=_get_domain_product_tmpl_id
    )
    telecom_service_name = fields.Char('Telecom Service Name', related='product_tmpl_id.name', readonly=True)
    
    # Telecom Service Category
    category_id = fields.Many2one('product.category', 'Product Category', related='product_tmpl_id.categ_id', store=True, readonly=True, index=True)
    category_name = fields.Char('Category Name', related='category_id.name', readonly=True)
    category_code = fields.Char('Category Code', related='category_id.code', store=True, readonly=True, index=True)

    # Telecom Service Consumption
    consumption_timestamp = fields.Datetime('Consumption Timestamp', required=True, default=fields.Datetime.now, index=True)
    consumption_reference = fields.Char('Telecom Service Consumption Reference', related='product_tmpl_id.default_code', readonly=True)
    consumption_qty = fields.Integer('Consumption Quantity', required=True, default=1)

    @api.depends('telecom_service_name', 'consumption_timestamp')
    def _compute_name(self):
        for record in self:
            record.name = '%s - %s' % (record.telecom_service_name, record.consumption_timestamp)
    
    @api.constrains('product_tmpl_id')
    def _check_product_tmpl_id(self):
        for record in self:
            if not record.product_tmpl_id:
                raise ValueError(_('Telecom Service Template is required'))
            if not record.product_tmpl_id.categ_id.parent_id.id == self.env.ref('somit_telecom.product_category_telecom').id:
                raise ValueError(_('Telecom Service Template must be a Telecom Service'))
            
    @api.constrains('consumption_qty')
    def _check_consumption_qty(self):
        for record in self:
            if record.consumption_qty <= 0:
                raise ValueError(_('Consumption Quantity must be greater than 0'))
            
    @api.onchange('consumption_qty')
    def _onchange_consumption_qty(self):
        if self.consumption_qty <= 0:
            self.consumption_qty = 1

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('consumption_timestamp', False):
                vals['consumption_timestamp'] = parse_dates(vals['consumption_timestamp'])
            if vals.get('product_tmpl_id', False) and vals.get('consumption_timestamp', False):
                vals['name'] = '%s - %s' % (self.env['product.template'].browse(vals['product_tmpl_id']).name, vals['consumption_timestamp'])
        
        return super(TelecomServiceConsumption, self).create(vals_list)
    
    def write(self, vals):
        if vals.get('consumption_timestamp', False):
            vals['consumption_timestamp'] = parse_dates(vals['consumption_timestamp'])
        
        return super(TelecomServiceConsumption, self).write(vals)