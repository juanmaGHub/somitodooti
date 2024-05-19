##############################################################################
#    Som IT Odoo Telecom Custom Addons
##############################################################################
{
    "name": "Som IT Telecom Custom Addons",
    "version": "16.0.1.0.0",
    "description": """
        - Custom Addons for Som IT Telecom Management Module
    """,
    "author": "Som IT Cooperatiu",
    "license": "AGPL-3",
    "depends": [
        "base",
        "product",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/product_data.xml",
        "views/telecom_service_consumption_views.xml",
    ],
    "demo": [
        'demo/demo_consumptions.xml',
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}