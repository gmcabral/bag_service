# -*- coding: utf-8 -*-
from osv import fields, osv, orm
import re

ZONE_SELECTION=[('none','Ninguna'),('Zona1','Zona1'),
			('Zona2','Zona2'),('Zona3','Zona3'),
			('Zona4','Zona4'),('Zona5','Zona5'),
			('Zona6','Zona6')]

PHONE_REX=re.compile('^\d+$',re.I)

class adapta_res_partner(osv.osv):
	_name = 'res.partner'
	_inherit = 'res.partner'
	_description = 'Adaptaciones a Partners'

	def name_get(self, cr, uid, ids, context={}):
		if not len(ids):
			return []
		reads = self.read(cr, uid, ids, ['name', 'lastname'], context)
		res = []
		for record in reads:
			name = record['name']
			if record['lastname']:
				name = record['lastname'] + ', '+name
			res.append((record['id'], name))
		return res

	def _get_phone_str(self, cr, uid, ids, field_name, arg, context):
		res = {}
		partner = self.pool.get('res.partner').browse(cr, uid, ids)
		phone_str = None		 	
		if partner[0].mobile and partner[0].phone:
			phone_str = partner[0].phone + " / " + partner[0].mobile 	 
		else:
			if partner[0].phone:
				phone_str = str(partner[0].phone)
			if partner[0].mobile:
				phone_str = str(partner[0].mobile)	

		res[partner[0].id]=phone_str
		return res
	
	_columns = {
		'lastname': fields.char('Name', size=128, select=True),
		'street_num' : fields.integer('Nro'),
		'piso_dpto' : fields.char('Piso/Dpto', size=128),
		'zona': fields.selection(ZONE_SELECTION, 'Zona'),
		'phone_str': fields.function(_get_phone_str, type='char',size='128', string='Telefonos',store=False,readonly=True),
	}

	_defaults = {
	}

	def _check_phone_number(self, cr, uid, ids, context=None):
		
		record = self.browse(cr, uid, ids, context=context)
		for data in record:
			if data.phone != False:
				if PHONE_REX.match(data.phone):
					return True
				else:
					return False
			if data.mobile != False:
				if PHONE_REX.match(data.mobile):
					return True
				else:
					return False
		return True
	
	_constraints = [(_check_phone_number, '\nError: El numero de telefono debe ser numerico', ['phone','mobile']), ]

adapta_res_partner()

