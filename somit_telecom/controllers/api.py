import logging
from datetime import datetime

from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied, UserError

from ..commons.utils import parse_dates


_logger = logging.getLogger(__name__)

# API Constants
SERVICE_CONSUMPTIONS_LIMIT = 100

# API Model
WRITEABLE_FIELDS = ['product_tmpl_id', 'company_id', 'consumption_timestamp', 'consumption_qty'] 

# API Messages
ACCESS_DENIED_MSG = 'Authentication failed. Check your credentials or contact the system administrator.'
INVALID_FIELD_MSG = 'Invalid field name provided for Telecom service consumption. Check the API documentation for the correct field names.'
MISSING_TELECOM_SERVICE_MSG = 'To create a consumption you must provide a Telecom Service Template ID or Name.'
MISSING_CONSUMPTION_QTY_MSG = 'To create a consumption you must provide a consumption quantity.'
UNKNOWN_TELECOM_SERVICE_MSG = 'The Telecom Service Template ID or Name provided does not exist.'
CONSUMPTION_NOT_FOUND_MSG = 'Consumption not found. Check the ID provided and try again.'
INVALID_DATE_FORMAT_MSG = 'Invalid date format or missing required date.'
INVALID_COMPANY_MSG = 'Invalid company ID provided. Using the current user\'s company instead.'
INVALID_CONSUMPTION_QTY_MSG = 'Invalid consumption quantity provided. Check the quantity and try again.'

# Log Messages
LOGGING_MSG = 'User %s successfully authenticated'
LOGGING_FAILED_MSG = 'Authentication failed for user %s'


class TelecomServiceAPI(http.Controller):
    def _authorize_external_call(self, req, **kwargs):
        db = kwargs.get('db', request.env.cr.dbname)
        login = kwargs.get('login', False)
        password = kwargs.get('password', False)

        try:
            uid = req.session.authenticate(db, login, password)
            _logger.info(LOGGING_MSG, login)
            return uid
        except:
            _logger.error(LOGGING_FAILED_MSG, login)
            raise AccessDenied(message=ACCESS_DENIED_MSG)
        
    def _validate_telecom_service(self, req, kwargs, create=False):
        ProductTemplate = req.env['product.template']

        # Check if Telecom Service Template ID or Name is provided
        if not kwargs.get('product_tmpl_id', False) and not kwargs.get('telecom_service_name', False) and create:
            raise UserError(MISSING_TELECOM_SERVICE_MSG)
        elif not kwargs.get('product_tmpl_id', False) and not kwargs.get('telecom_service_name', False) and not create:
            return
        
        # Validate provided Telecom Service Template ID or Name
        product_tmpl_id = ProductTemplate.search([('id', '=', int(kwargs.get('product_tmpl_id', False)))]).id
        if not product_tmpl_id:
            telecom_service_name = kwargs.get('telecom_service_name', False)
            if telecom_service_name:
                product_tmpl_id = ProductTemplate.search([
                    ('name', '=', str(telecom_service_name).strip())
                ], limit=1).id
        
        if not product_tmpl_id:
            raise UserError(UNKNOWN_TELECOM_SERVICE_MSG)
        
        kwargs['product_tmpl_id'] = product_tmpl_id

    def _validate_company_id(self, req, uid, kwargs, create=False):
        ResCompany = req.env['res.company']
        ResUsers = req.env['res.users']

        if not kwargs.get('company_id', False) and not create:
            return

        # If not provided or invalid, use the current user's company
        company_id = ResCompany.search([('id', '=', int(kwargs.get('company_id', False)))]).id
        if not company_id:
            _logger.warning(INVALID_COMPANY_MSG)
            company_id = ResUsers.browse(uid).company_id.id
        
        kwargs['company_id'] = company_id

    def _validate_consumption_timestamp(self, kwargs, create=False):
        if not kwargs.get('consumption_timestamp', False) and create:
            raise UserError(INVALID_DATE_FORMAT_MSG)
        elif not kwargs.get('consumption_timestamp', False) and not create:
            return
        else:
            kwargs['consumption_timestamp'] = parse_dates(kwargs['consumption_timestamp'])
            if not kwargs['consumption_timestamp']:
                raise UserError(INVALID_DATE_FORMAT_MSG)
            
    def _validate_consumption_qty(self, kwargs, create=False):
        if not kwargs.get('consumption_qty', False) and create:
            raise UserError(MISSING_CONSUMPTION_QTY_MSG)
        elif not kwargs.get('consumption_qty', False) and not create:
            return
        else:
            try:
                kwargs['consumption_qty'] = int(kwargs['consumption_qty'])
            except:
                raise UserError(INVALID_CONSUMPTION_QTY_MSG)

    def _validate_write_operations(self, req, uid, kwargs, create=False):
        self._validate_telecom_service(req, kwargs, create)
        self._validate_company_id(req, uid, kwargs, create)
        self._validate_consumption_timestamp(kwargs, create)
        self._validate_consumption_qty(kwargs, create)
        

    # -- REST API CRUD Operations --
    @http.route('/telecomservice/api/consumption/create', type='json', auth='none', methods=['POST'])
    def create_consumption(self, **kwargs):
        uid = self._authorize_external_call(request, **kwargs)
        self._validate_write_operations(request, uid, kwargs, create=True)
        
        # Filter out non-writeable fields
        vals = {key: kwargs[key] for key in kwargs.keys() if key in WRITEABLE_FIELDS}

        consumption = request.env['telecom.service.consumption'].create(vals)
        return consumption.read()
    
    @http.route('/telecomservice/api/consumption/<int:id>', type='json', auth='none', methods=['POST'])
    def get_consumption(self, id, **kwargs):
        self._authorize_external_call(request, **kwargs)
        
        return request.env['telecom.service.consumption'].browse(id).read()
    
    @http.route('/telecomservice/api/consumption/list', type='json', auth='none', methods=['POST'])
    def get_consumption_list(self, **kwargs):
        self._authorize_external_call(request, **kwargs)
        
        limit = kwargs.get('limit', SERVICE_CONSUMPTIONS_LIMIT)
        offset = kwargs.get('offset', 0)
        date_filter = parse_dates(kwargs.get('date_filter', False))
        
        domain = [('consumption_timestamp', '>=', date_filter)] if date_filter else []
        return request.env['telecom.service.consumption'].search(
            domain, 
            limit=limit, 
            offset=offset, 
            order=request.env['telecom.service.consumption']._order
        ).read()
    
    @http.route('/telecomservice/api/consumption/update/<int:id>', type='json', auth='none', methods=['POST'])
    def update_consumption(self, id, **kwargs):
        uid = self._authorize_external_call(request, **kwargs)
        self._validate_write_operations(request, uid, kwargs)
        
        consumption = request.env['telecom.service.consumption'].search([('id', '=', id)])
        if not consumption:
            raise UserError(CONSUMPTION_NOT_FOUND_MSG)
        
        vals = {key: kwargs[key] for key in kwargs.keys() if key in WRITEABLE_FIELDS}

        consumption.write(vals)
        return consumption.read()
    
    @http.route('/telecomservice/api/consumption/delete/<int:id>', type='json', auth='none', methods=['POST'])
    def delete_consumption(self, id, **kwargs):
        self._authorize_external_call(request, **kwargs)
        
        consumption = request.env['telecom.service.consumption'].search([('id', '=', id)])
        if not consumption:
            raise UserError(CONSUMPTION_NOT_FOUND_MSG)
        
        consumption.unlink()
        return True
    