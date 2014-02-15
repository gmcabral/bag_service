# -*- coding: utf-8 -*-
{
    'name': 'bag_service',
    'version': '1.0',
    'category': 'Bag_Service',
    'description': """
Modulo Reparaciones
""",
    'author': 'Moxotoro',
    'maintainer': 'Moxotoro',
    'website': '',
    'depends': ['web'],
    'css':['static/src/css/service_order_form_label.css','static/src/css/style.css'],
	'qweb' : ['static/src/xml/base.xml'],
    'js': ['static/src/js/first_module.js'],
	'init_xml' : [],
	'update_xml' : ['bag_service_view.xml','bag_wzd_facturar.xml',
                    'bag_wzd_estanterias.xml','bag_wzd_cambiar_estados.xml','bag_wzd_hoja_ruta.xml','bag_wzd_resumen.xml',
                    'bag_work_workflow.xml','bag_sequence.xml','bag_service_report_view.xml',
                    'security/bag_service_security.xml','bag_res_partner_view.xml'],
    'installable': True,
	'active' : True,
    'auto_install': False,
 
}
