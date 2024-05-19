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

# API Log Messages
LOGGING_MSG = 'User %s successfully authenticated'
LOGGING_FAILED_MSG = 'Authentication failed for user %s'
LOGOUT_MSG = 'User successfully logged out'

# API Access Messages
ACCESS_DENIED_MSG = 'Authentication failed. Check your credentials or contact the system administrator.'

class TelecomServiceAPIV2(http.Controller):        
    @http.route('/telecomservice/api/v2/authenticate', type='json', auth='none', methods=['POST'])
    def authenticate(self, **kwargs):
        db = kwargs.get('db', request.env.cr.dbname)
        login = kwargs.get('login', False)
        password = kwargs.get('password', False)

        try:
            request.session.authenticate(db, login, password)
            _logger.info(LOGGING_MSG, login)

            return request.session.sid
        except:
            _logger.error(LOGGING_FAILED_MSG, login)
            raise AccessDenied(message=ACCESS_DENIED_MSG)
        
    @http.route('/telecomservice/api/v2/logout', type='json', auth='user', methods=['POST'])
    def logout(self, **kwargs):
        request.session.logout()
        _logger.info(LOGOUT_MSG)
        return True

    @http.route('/telecomservice/api/v2/consumption/create', type='json', auth='user', methods=['POST'])
    def create_consumption(self, **kwargs):
        return request.env['telecom.api.service'].create_consumption(**kwargs)
        
    @http.route('/telecomservice/api/v2/consumption/<int:id>', type='json', auth='user', methods=['GET'])
    def get_consumption(self, id, **kwargs):
        return request.env['telecom.api.service'].get_consumption(id)
    
    @http.route('/telecomservice/api/v2/consumption/list', type='json', auth='user', methods=['GET'])
    def list_consumptions(self, **kwargs):
        return request.env['telecom.api.service'].get_consumption_list(**kwargs)
    
    @http.route('/telecomservice/api/v2/consumption/update/<int:id>', type='json', auth='user', methods=['PUT'])
    def update_consumption(self, id, **kwargs):
        return request.env['telecom.api.service'].update_consumption(id, **kwargs)
    
    @http.route('/telecomservice/api/v2/consumption/delete/<int:id>', type='json', auth='user', methods=['DELETE'])
    def delete_consumption(self, id, **kwargs):
        return request.env['telecom.api.service'].delete_consumption(id)