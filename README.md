# somitodooti
Som IT Odoo technical interview solution

## Rest API Documentation
https://docs.google.com/document/d/1N7CxpubasjstIU9p2VPXfLzy26fj_qglxu-ukJyt4mc/edit?usp=sharing
Generated using Postman

### Usage notes:
```
import json
import requests

url = f'http://{host}:{port}/telecomservice/api/v2/authenticate'
data = {
    "jsonrpc": "2.0",
    "params": {
        "login": "user",
        "password": "pass"
    }
}
headers = {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}
response = requests.post(url, headers=headers, data=json.dumps(data))

# use this cookies to validate future requests 
cookies = response.cookies

readurl = f'http://{host}:{port}/telecomservice/api/v2/consumption/{id}'
response = requests.get(readurl, headers=headers, data=json.dumps({}), cookies=cookies)
```
See also this module's tests.


There are also tests to check the API endpoints, but they rely on the demo data, which needs to be
improved.

## Link to Odoo Technical Interview Data
https://gitlab.com/somitcoop/interview/odoo-technical-interview-data
The consumption timestamp field was declared as Datetime, but every possible date format is allowed.
See commons/utils.py