{
    'name': 'Delete Invoice(paid and cancelled)',
    'version': '14.0',
    'category': 'Accounting',
    'summary': 'Force delete invoices(paid invoice,posted invoice and cancelled invoice) and payments',
    'description': """
        Used can delete paid and cancelled invoices and related payments
    """,
    'depends': ['account'],
    'data': [
        'views/account_move_view.xml',
    ],
    'author': 'Teqstars',
    'website': 'https://teqstars.com',
    'support': 'support@teqstars.com',
    'maintainer': 'Teqstars',
    'images': ['static/description/delete_posted_invoice_banner.png'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
    'price': '5.0',
    'currency': 'EUR',
}