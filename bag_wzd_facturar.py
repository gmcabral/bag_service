# -*- coding: utf-8 -*-
from osv import fields, osv, orm
import time
import decimal_precision as dp

class wizard_facturar(osv.osv_memory):
	_name = 'bag.wzd_facturar'
	_description = 'Facturar'

	_columns = {
		'resumen_ids': fields.one2many('repair.wizard_facturar_resumen_ids', 'wizard_facturar_id', 'Resumenes'),                               
		'factura': fields.char('Factura', size=64), 
	}
    
	def facturar(self, cr, uid, ids, context=None):
		data  = self.browse(cr, uid, ids)[0]

		order_obj = self.pool.get('bag.service')
		
		#primero controlar si las ordenes del resumen se encuentran en estado entregado sino no se puede facturar
		
		estado_obj = self.pool.get('bag.state')
		estado_id = estado_obj.search(cr, uid, [('name', '=', 'Entregado')])
		
		for resumen in data.resumen_ids:                    
			order_ids = order_obj.search(cr, uid, [('summary_number', '=', resumen.resumen),('state_id','!=',estado_id[0])])
		
		
		#se setea el numero de factura
		if order_ids:
			mensaje = 'se indicaron resumenes que contienen ordenes que no estan en estado Entregado'
			raise osv.except_osv(('No es posible facturar') ,mensaje)

		
		for resumen in data.resumen_ids:                    
			order_ids = order_obj.search(cr, uid, [('summary_number', '=', resumen.resumen)])
			order_obj.write(cr, uid, order_ids, {'invoiced': True, 'invoice_number': data.factura})
                    
                
		return {
			'type': 'ir.actions.act_window_close',
		}

	def anular(self, cr, uid, ids, context=None):
		#print "anular"
        
		data  = self.browse(cr, uid, ids)[0]
        
		#print "ids", ids
		#print "data", data
                
		order_obj = self.pool.get('bag.service')
                    
		for resumen in data.resumen_ids:                    
			order_ids = order_obj.search(cr, uid, [('summary_number', '=', resumen.resumen)])
			order_obj.write(cr, uid, order_ids, {'invoiced': False, 'invoice_number': None})
                    
                
		return {
			'type': 'ir.actions.act_window_close',
		}

wizard_facturar()

class wizard_facturar_resumen_ids(osv.osv_memory):
	_name = 'repair.wizard_facturar_resumen_ids'

	_columns = {
		'resumen': fields.char('Resumen',size=64),
		'wizard_facturar_id': fields.many2one('bag.wzd_facturar', 'Facturar'),                         
	}

wizard_facturar_resumen_ids()

"""
class bag_facturar(osv.osv_memory):
	_name = 'bag.facturar'
	_description = 'Facturar'

	_columns = {
			'summary_number': fields.char('Nro. Resumen',size=32),
	}
	def facturar(self, cr, uid, ids, context=None):
		#print "facturar"
        
		data  = self.browse(cr, uid, ids)[0]
        
 		#print "ids", ids
		#print "data", data
                
		order_obj = self.pool.get('bag.service')
        
		total = 0
        
		for order in order_obj.browse(cr, uid, ids):
			total += order.price

		factura = self.pool.get('ir.sequence').get(cr, uid, 'factura')
		order_obj.write(cr, uid, ids, {'invoice_number': detalle, 'invoiced': True})
                    
		return {
			'type': 'ir.actions.act_window_close',
		}

bag_facturar() """

