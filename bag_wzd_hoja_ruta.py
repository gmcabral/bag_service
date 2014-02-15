# -*- coding: utf-8 -*-
from osv import fields, osv, orm
import time
import decimal_precision as dp

class wizard_marca_hoja_ruta(osv.osv_memory):
	_name = 'bag.wzd_marca_hoja_ruta'
	_description = 'Marca Hojas de Ruta'

	def marca_hoja_ruta(self, cr, uid, ids, context=None):
        
		order_obj = self.pool.get('bag.service')
		active_ids = context and context.get('active_ids', [])
                                        
		order_obj.write(cr, uid, active_ids, {'marca_hoja_ruta': True})
                
		return {
			'type': 'ir.actions.act_window_close',
		}

wizard_marca_hoja_ruta()

class wizard_desmarca_hoja_ruta(osv.osv_memory):
	_name = 'bag.wzd_desmarca_hoja_ruta'
	_description = 'Desmarca Hojas de Ruta'

	def desmarca_hoja_ruta(self, cr, uid, ids, context=None):
        
		order_obj = self.pool.get('bag.service')
		active_ids = context and context.get('active_ids', [])
                                        
		order_obj.write(cr, uid, active_ids, {'marca_hoja_ruta': False})
                
		return {
			'type': 'ir.actions.act_window_close',
		}

wizard_desmarca_hoja_ruta()

