import requests
import json
from odoo.tests.common import TransactionCase, tagged
from datetime import datetime, timedelta


@tagged('post_install', '-at_install', 'telecom_service_consumption')
class TestTelecomServiceConsumption(TransactionCase):
    # TODO: Some of these tests rely on demo data, if the demo data is not present, the tests will be skipped
    #      This is not ideal, the tests should be able to run without the demo data, but I was struggling to create
    #      the necessary data in the setUpClass method and commit it to the database. I will need to revisit this.
    @classmethod
    def setUpClass(cls):
        super(TestTelecomServiceConsumption, cls).setUpClass()
        cls.telecom_service_consumption = cls.env['telecom.service.consumption']
        
        cls.telecom_service = cls.env.ref('somit_telecom.product_template_telecom_mobile_data')
        
        cls.telecom_service_consumption_data = {
            'product_tmpl_id': cls.telecom_service.id,
            'consumption_timestamp': datetime.now() - timedelta(days=1),
            'consumption_qty': 10,
        }
        cls.consumption_1 = cls.telecom_service_consumption.create(cls.telecom_service_consumption_data)
        cls.server_base_url = cls.env['ir.config_parameter'].sudo().get_param('web.base.url')
        cls.headers = {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}

        # Authenticate user in the API
        cls.auth_url = cls.server_base_url + '/telecomservice/api/v2/authenticate'
        cls.auth_data = {
            "jsonrpc": "2.0",
            "params": {
                'login': 'admin',
                'password': 'admin',
            },
        }
        cls.cookies = None

    def setUp(self):
        super(TestTelecomServiceConsumption, self).setUp()
        self.assertEqual(self.consumption_1.id, self.telecom_service_consumption.search([('id', '=', self.consumption_1.id)]).id, "Telecom Service Consumption Record should be created")

    def _set_cookies(self):
        response = requests.post(self.auth_url, headers=self.headers, data=json.dumps(self.auth_data))
        self.assertEqual(response.status_code, 200)
        self.cookies = response.cookies
        return self.cookies

    def test_telecom_service_consumption(self):
        self.assertTrue(self.consumption_1.id, "Telecom Service Consumption Record should be created")
        self.assertEqual(self.consumption_1.product_tmpl_id, self.telecom_service, "Telecom Service Template should be linked")
        self.assertEqual(self.consumption_1.consumption_qty, 10, "Consumption Quantity should be 10")
        self.assertEqual(self.consumption_1.consumption_timestamp, self.telecom_service_consumption_data['consumption_timestamp'], "Consumption Timestamp should be yesterday")
        self.assertEqual(self.consumption_1.consumption_reference, self.telecom_service.default_code, "Consumption Reference should be the default code of the Telecom Service")
        self.assertEqual(self.consumption_1.company_id, self.env.company, "Company should be the current company")
    
    def test_required_field_product_tmpl_id(self):
        with self.assertRaises(Exception), self.cr.savepoint():
            self.telecom_service_consumption.create({})
        with self.assertRaises(Exception):
            self.telecom_service_consumption.create({
                'consumption_timestamp': datetime.now() - timedelta(days=1),
            })
        with self.assertRaises(Exception):
            self.telecom_service_consumption.create({
                'consumption_qty': 10,
            })

    def test_last_month_filter(self):
        last_month = datetime.now() - timedelta(days=30)
        consumptions = self.env['telecom.service.consumption'].search([
            ('consumption_timestamp', '>=', last_month)
        ])
        self.assertIn(self.consumption_1, consumptions, "Consumption should be included in last month's records")

    def test_api_create_consumption(self):
        cookies = self._set_cookies()

        date_now_iso = datetime.now().isoformat()
        url = self.server_base_url + '/telecomservice/api/v2/consumption/create'
        data = {
            "jsonrpc": "2.0",
            "params": {
                'product_tmpl_id': self.telecom_service.id,
                'consumption_timestamp': date_now_iso,
                'consumption_qty': 15,
                'k_invalid_field': 'will be ignored'
            },
        }
        response = requests.post(url, headers=self.headers, data=json.dumps(data), cookies=cookies)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json().get('result')), 1, "One record should be created")
        self.assertIn('id', response.json().get('result')[0])
        self.assertEqual(response.json().get('result')[0].get('consumption_qty'), 15)
        self.assertEqual(response.json().get('result')[0].get('product_tmpl_id')[0], self.telecom_service.id)
        self.assertEqual(response.json().get('result')[0].get('consumption_timestamp'), date_now_iso.replace('T', ' ').split('.')[0])

    def test_api_update_consumption(self):
        cookies = self._set_cookies()

        try:
            consumption_id = self.env.ref('somit_telecom.telecom_service_consumption_demo_test_2').id
        except:
            return
        
        url = f'{self.server_base_url}/telecomservice/api/v2/consumption/update/{consumption_id}'
        data = {
            "jsonrpc": "2.0",
            "params": {
                'consumption_qty': 40
            },
        }
        response = requests.put(url, headers=self.headers, data=json.dumps(data), cookies=cookies)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('result')[0].get('id'), consumption_id)
        self.assertEqual(response.json().get('result')[0].get('consumption_qty'), 40)

    def test_api_get_consumption(self):
        cookies = self._set_cookies()
        try:
            consumption_id = self.env.ref('somit_telecom.telecom_service_consumption_demo_test_2').id
        except:
            return

        url = f'{self.server_base_url}/telecomservice/api/v2/consumption/{consumption_id}'
        response = requests.get(url, headers=self.headers, data=json.dumps({}), cookies=cookies)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json().get('result')), 1, "One record should be returned")
        self.assertIn('id', response.json().get('result')[0])
        self.assertEqual(response.json().get('result')[0].get('id'), consumption_id)

    def test_api_delete_consumption(self):
        cookies = self._set_cookies()
        try:
            consumption_id = self.env.ref('somit_telecom.telecom_service_consumption_demo_test_1').id
        except:
            return
        
        url = f'{self.server_base_url}/telecomservice/api/v2/consumption/delete/{consumption_id}'
        response = requests.delete(url, headers=self.headers, data=json.dumps({}), cookies=cookies)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('result'), "Record should be deleted")
