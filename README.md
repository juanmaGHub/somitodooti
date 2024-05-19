# somitodooti
Som IT Odoo technical interview solution

## Rest API Documentation
https://docs.google.com/document/d/1N7CxpubasjstIU9p2VPXfLzy26fj_qglxu-ukJyt4mc/edit?usp=sharing
There are also tests to check the API endpoints, but they rely on the demo data, which needs to be
improved.
Every request should pass the basic auth credentials, that's why all request methods are posts.
TODO: Implement better auth (e.g. token based)

## Link to Odoo Technical Interview Data
https://gitlab.com/somitcoop/interview/odoo-technical-interview-data
The consumption timestamp field was declared as Datetime, but every possible date format is allowed.
See commons/utils.py