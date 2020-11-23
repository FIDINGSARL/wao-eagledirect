{
    'name' : 'Quote Calculator',
    'version': '1.0',
    'Summary': 'Quote Calculations for custom Sales and Purchase Modules',
    'description': 'To add new fields in the existing modules',
    'license': 'LGPL-3',
    'depends': [
        'sale_management',
        'purchase'
    ],    
    'data': [
        'views/quote_calculator_view.xml'
    ],
    'installable': True,
    'application':True,
    'auto_install':False
}