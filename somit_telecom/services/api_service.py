from odoo import models, api
from odoo.exceptions import UserError, AccessDenied

from ..commons.utils import parse_dates


# API Model
WRITEABLE_FIELDS = ['product_tmpl_id', 'company_id', 'consumption_timestamp', 'consumption_qty'] 

# API Messages
ACCESS_DENIED_MSG = 'Authentication failed. Check your credentials or contact the system administrator.'
INVALID_COMPANY_MSG = 'Invalid company ID provided. Using the current user\'s company instead.'
INVALID_TELECOM_SERVICE_MSG = 'Invalid Telecom Service Template ID or Name provided. Check the ID or Name and try again.'
UNKNOWN_TELECOM_SERVICE_MSG = 'The Telecom Service Template ID or Name provided does not exist.'
INVALID_DATE_FORMAT_MSG = 'Invalid date format.'
INVALID_CONSUMPTION_QTY_MSG = 'Invalid consumption quantity provided. Check the quantity and try again.'
MISSING_TELECOM_SERVICE_MSG = 'To create a consumption you must provide a Telecom Service Template ID or Name.'
MISSING_COMPANY_MSG = 'Missing company ID. Using the current user\'s company instead.'
MISSING_CONSUMPTION_QTY_MSG = 'To create a consumption you must provide a consumption quantity.'
MISSING_DATE_MSG = 'To create a consumption you must provide a consumption timestamp.'
MISSING_CONSUMPTION_MSG = 'Consumption not found. Check the ID provided and try again.'

class TelecomAPIService(models.AbstractModel):
    _name = 'telecom.api.service'

    def _validate_telecom_service(self, kwargs, create=False):
        """
            Validate Telecom Service Template ID or Name
            Update vals with the correct product_tmpl_id or raise an error
        """
        ProductTemplate = self.env['product.template']
        
        product_tmpl_id = kwargs.get('product_tmpl_id', False)
        telecom_service_name = kwargs.get('telecom_service_name', False)

        if not product_tmpl_id and not telecom_service_name and create:
            raise UserError(MISSING_TELECOM_SERVICE_MSG)
        elif not product_tmpl_id and not telecom_service_name and not create:
            return
        else:
            try: 
                product_tmpl_id = int(product_tmpl_id)
            except:
                raise UserError(INVALID_TELECOM_SERVICE_MSG)
            
            product_tmpl_id = ProductTemplate.search([
                ('id', '=', product_tmpl_id),
                ('categ_id.parent_id', '=', self.env.ref('somit_telecom.product_category_telecom').id)
            ]).id
            if not product_tmpl_id:
                # Search by name
                telecom_service_name = str(telecom_service_name).strip()
                if telecom_service_name:
                    product_tmpl_id = ProductTemplate.search([
                        ('name', '=', telecom_service_name)
                    ], limit=1).id

            if not product_tmpl_id:
                raise UserError(UNKNOWN_TELECOM_SERVICE_MSG)

            kwargs['product_tmpl_id'] = product_tmpl_id

    def _validate_company_id(self, kwargs, create=False):
        """
            Validate Company ID
            Update vals with the correct company_id or use the current user's company.
            This method is used to validate the company_id field in the vals dictionary it does not raise an error.
        """
        ResCompany = self.env['res.company']

        company_id = kwargs.get('company_id', False)
        if not company_id and not create:
            return
        elif not company_id and create:
            company_id = self.env.user.company_id.id
        else:
            try:
                company_id = int(company_id)
            except:
                company_id = self.env.user.company_id.id
            

            company_id = ResCompany.search([('id', '=', company_id)]).id
            if not company_id:
                company_id = self.env.user.company_id.id

            kwargs['company_id'] = company_id

    def _validate_consumption_timestamp(self, kwargs, create=False):
        """
            Validate Consumption Timestamp
            Update vals with the correct consumption_timestamp or raise an error
        """
        consumption_timestamp = kwargs.get('consumption_timestamp', False)
        if not consumption_timestamp and not create:
            return
        elif not consumption_timestamp and create:
            raise UserError(MISSING_DATE_MSG)
        else:
            consumption_timestamp = parse_dates(consumption_timestamp)
            if not consumption_timestamp:
                raise UserError(INVALID_DATE_FORMAT_MSG)

            kwargs['consumption_timestamp'] = consumption_timestamp

    def _validate_consumption_qty(self, kwargs, create=False):
        """
            Validate Consumption Quantity
            Update vals with the correct consumption_qty or raise an error
        """
        consumption_qty = kwargs.get('consumption_qty', False)
        if not consumption_qty and not create:
            return
        elif not consumption_qty and create:
            raise UserError(MISSING_CONSUMPTION_QTY_MSG)
        else:
            try:
                consumption_qty = int(consumption_qty)
                if consumption_qty <= 0:
                    raise UserError(INVALID_CONSUMPTION_QTY_MSG)
            except:
                raise UserError(INVALID_CONSUMPTION_QTY_MSG)

            kwargs['consumption_qty'] = consumption_qty

    def _validate_write_params(self, kwargs, create=False):
        """
            Validate Write Parameters
            Update vals with the correct values or raise an error
        """
        self._validate_company_id(kwargs, create)
        self._validate_telecom_service(kwargs, create)
        self._validate_consumption_qty(kwargs, create)
        self._validate_consumption_timestamp(kwargs, create)
            
    @api.model
    def create_consumption(self, **kwargs):
        Consumption = self.env['telecom.service.consumption']
        self._validate_write_params(kwargs, create=True)

        # Filter out non-writeable fields
        vals = {key: kwargs[key] for key in kwargs.keys() if key in WRITEABLE_FIELDS}

        consumption = Consumption.create(vals)
        return consumption.read()
    
    @api.model
    def get_consumption(self, id):
        Consumption = self.env['telecom.service.consumption']
        
        # Check that the consumption exists
        consumption_id = Consumption.search([('id', '=', id)], limit=1).id
        if not consumption_id:
            raise UserError(MISSING_CONSUMPTION_MSG)
        
        return Consumption.browse(id).read()
    
    @api.model
    def get_consumption_list(self, **kwargs):
        Consumption = self.env['telecom.service.consumption']
        limit = kwargs.get('limit', 10)
        offset = kwargs.get('offset', 0)
        date_filter = parse_dates(kwargs.get('date_filter', False))
        
        domain = [('consumption_timestamp', '>=', date_filter)] if date_filter else []
        return Consumption.search(
            domain,
            limit=limit,
            offset=offset,
            order=Consumption._order
        ).read()
    
    @api.model
    def update_consumption(self, id, **kwargs):
        Consumption = self.env['telecom.service.consumption']
        
        # Check that the consumption exists
        consumption_id = Consumption.search([('id', '=', id)], limit=1).id
        if not consumption_id:
            raise UserError(MISSING_CONSUMPTION_MSG)
        
        self._validate_write_params(kwargs)

        # Filter out non-writeable fields
        vals = {key: kwargs[key] for key in kwargs.keys() if key in WRITEABLE_FIELDS}

        consumption = Consumption.browse(id)
        consumption.write(vals)
        return consumption.read()
    
    @api.model
    def delete_consumption(self, id):
        Consumption = self.env['telecom.service.consumption']
        
        # Check that the consumption exists
        consumption_id = Consumption.search([('id', '=', id)], limit=1).id
        if not consumption_id:
            raise UserError(MISSING_CONSUMPTION_MSG)
        
        Consumption.browse(id).unlink()
        return True