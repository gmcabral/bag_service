# -*- coding: utf-8 -*-
from osv import fields, osv, orm
import time
import decimal_precision as dp

class wizard_marca_resumen(osv.osv_memory):
	_name = 'bag.wzd_marca_resumen'
	_description = 'Marca Resumen'

	def marca_resumen(self, cr, uid, ids, context=None):
        
		order_obj = self.pool.get('bag.service')
		active_ids = context and context.get('active_ids', [])
                                        
		order_obj.write(cr, uid, active_ids, {'marca_resumen': True})
                
		return {
			'type': 'ir.actions.act_window_close',
		}

wizard_marca_resumen()

class wizard_desmarca_resumen(osv.osv_memory):
	_name = 'bag.wzd_desmarca_resumen'
	_description = 'Desmarca Resumen'

	def desmarca_resumen(self, cr, uid, ids, context=None):
        
		order_obj = self.pool.get('bag.service')
		active_ids = context and context.get('active_ids', [])
                                        
		order_obj.write(cr, uid, active_ids, {'marca_resumen': False})
                
		return {
			'type': 'ir.actions.act_window_close',
		}

wizard_desmarca_resumen()

