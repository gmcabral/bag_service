# -*- coding: utf-8 -*-
from osv import fields, osv, orm
from tools.translate import _
import time
import decimal_precision as dp
import random
import string
import netsvc
import re

STATUS_LIST = [(), (), (), ]
ZONE_SELECTION = [('none', 'Ninguna'), ('z1', 'Zona1'),
									('z2', 'Zona2'), ('z3', 'Zona3'),
									('z4', 'Zona4'), ('z5', 'Zona5'),
									('z6', 'Zona6')]
IVA_VALUE = 0.21
ZONE_SELECTION_DICT = dict(ZONE_SELECTION)
FACTURA_REX = re.compile('^\d{4}[a-z]?\d{6}$', re.I)
# Clases que agrupan caracteristicas de las valijas
class bag_type(osv.osv):
	_name = 'bag.type'
	_description = 'Type'

	_columns = {
		'name': fields.char('Tipo' , size=32, required=True),
	}

bag_type()

class bag_format(osv.osv):
	_name = 'bag.format'
	_description = 'Format'

	_columns = {
		'name': fields.char('Formato', size=32, required=True),
	}
bag_format()

class bag_color(osv.osv):
	_name = 'bag.color'
	_description = 'Color'

	_columns = {
		'name': fields.char('Color', size=32, required=True),
	}
bag_color()

class bag_material(osv.osv):
	_name = 'bag.material'
	_description = 'Material'

	_columns = {
		'name': fields.char('Material', size=32, required=True),
	}
bag_material()

class bag_size(osv.osv):
	_name = 'bag.size'
	_description = 'Size'

	_columns = {
		'name': fields.char('Tamano', size=32, required=True),
	}
bag_size()
##########FIN CLASES DE CARACTERISTICAS

# ##Clases que definen otros objetos importantes
class bag_puestos_trabajo(osv.osv):
	_name = 'bag.puestos_trabajo'
	_description = 'Puestos de Trabajo'

	_columns = {
		'service_id': fields.many2one('bag.service', 'Orden de Reparacion', readonly=True, states={'draft':[('readonly', False)]}),
		'shelving_id': fields.many2one('bag.shelving', 'Puesto', readonly=True, states={'draft':[('readonly', False)]}),
		'work_done': fields.one2many('bag.puestos_trabajo_work_done', 'puestostrabajo_id', 'Trabajo realizado', readonly=True, states={'draft':[('readonly', False)]}),
		'work_made': fields.text('Nota en Reparacion', readonly=True, states={'draft':[('readonly', False)]}),
		'notas_orden': fields.related('service_id', 'quotation_notes', type='text'),
		'state': fields.selection([
			('draft', 'Borrador'),
			('confirmed', 'Confirmado'),
			], 'Estado', readonly=True),
	}

	_defaults = {
		'state': lambda *a: 'draft',
	}

	def onchange_service_id(self, cr, uid, ids, service_id, shelving_id):
		service = self.pool.get('bag.service').browse(cr, uid, service_id)
		works_to_be_done_ids = self.pool.get('bag.work_to_be_done').search(cr, uid, [('service_id', '=', service_id)])
		
		result = []
		notas = service.quotation_notes
		if shelving_id:
			for work_to_be_done_id in works_to_be_done_ids:
				work_to_be_done_obj = service = self.pool.get('bag.work_to_be_done').browse(cr, uid, work_to_be_done_id)
				# se carga cualquier trabajo menos gastos administrativos porque es un trabajo que no deben realizar
				if work_to_be_done_obj.work_id.name != 'GASTO ADMINISTRATIVO':
					result.append((0, 0, {'work_id' : work_to_be_done_obj.work_id.id, 'quantity' : work_to_be_done_obj.quantity, 'puestostrabajo_id' : shelving_id}))
		return {'value': {'work_done': result, 'notas_orden':notas}}

	def onchange_shelving_id(self, cr, uid, ids, service_id, shelving_id):
		service = self.pool.get('bag.service').browse(cr, uid, service_id)
		works_to_be_done_ids = self.pool.get('bag.work_to_be_done').search(cr, uid, [('service_id', '=', service_id)])
		
		result = []
		notas = service.quotation_notes
		if service_id:
			for work_to_be_done_id in works_to_be_done_ids:
				work_to_be_done_obj = service = self.pool.get('bag.work_to_be_done').browse(cr, uid, work_to_be_done_id)
				# se carga cualquier trabajo menos gastos administrativos porque es un trabajo que no deben realizar
				if work_to_be_done_obj.work_id.name != 'GASTO ADMINISTRATIVO':
					result.append((0, 0, {'work_id' : work_to_be_done_obj.work_id.id, 'quantity' : work_to_be_done_obj.quantity, 'puestostrabajo_id' : shelving_id}))
		return {'value': {'work_done': result, 'notas_orden':notas}}
 

	def trabajo_realizado(self, cr, uid, ids, context=None):
		print "trabajo realizado"

		data = self.browse(cr, uid, ids)[0]
#
# 		print "ids", ids
# 		print "data", data

		order_obj = self.pool.get('bag.service')
		work_done_obj = self.pool.get('bag.work_done')

		if data.service_id.modificaciones_detalle:
			detalle = data.service_id.modificaciones_detalle
		else:
			detalle = ""

		detalle = detalle + '\n\nUsuario: %s\n' % (self.pool.get('res.users').browse(cr, uid, uid).name) + 'Cambio de Estanteria:  ' + time.strftime('%d/%m/%Y %H:%M:%S') + ' a ' + data.shelving_id.name + '\nCambio de Estado:  '	 + time.strftime('%d/%m/%Y %H:%M:%S') + ' a ' + data.shelving_id.state_id.name

		order_obj.write(cr, uid, [data.service_id.id], {'modificaciones_detalle': detalle, 'shelving_id': data.shelving_id.id, 'state_id': data.shelving_id.state_id.id, 'work_made': data.work_made})

		airline_obj = self.pool.get('bag.airline')
		airline = airline_obj.browse(cr, uid, data.service_id.airline_id.id)

		work_obj = self.pool.get('bag.work')

		for line in data.work_done:
			# solo los trabajos que se tildaron como realizados
			if line.trabajo_realizado:
				work_ids = work_done_obj.search(cr, uid, [('service_id', '=', data.service_id.id), ('work_id', '=', line.work_id.id)])

				work = work_obj.browse(cr, uid, line.work_id.id)

				if len(work_ids) > 0:
	
					desc = 0.7
	
					quantity = work_done_obj.read(cr, uid, work_ids[0], ['quantity'])['quantity'] + 1
	
					if airline.pricelist == 1:
						price = work.price + (quantity - 1) * work.price * desc
	
					if airline.pricelist == 2:
						price = work.price2 + (quantity - 1) * work.price2 * desc
	
					if airline.pricelist == 3:
						price = work.price3 + (quantity - 1) * work.price3 * desc
	
					work_done_obj.write(cr, uid, work_ids[0], {'quantity':quantity, 'price':price})
	
				else:
	
					if airline.pricelist == 1:
						price = work.price
	
					if airline.pricelist == 2:
						price = work.price2
	
					if airline.pricelist == 3:
						price = work.price3
	
					vals = {'service_id': data.service_id.id, 'work_id': line.work_id.id, 'quantity': 1, 'price': price}
					work_done_obj.create(cr, uid, vals)

		return True

bag_puestos_trabajo()


class bag_puestos_trabajo_work_done(osv.osv):
	_name = 'bag.puestos_trabajo_work_done'
	_description = 'Puestos de Trabajo Work Done'

	_columns = {
		'work_id': fields.many2one('bag.work', 'Work'),
		'quantity': fields.integer('Cantidad'),
		'puestostrabajo_id': fields.many2one('bag.puestos_trabajo', 'Puesto'),
		'trabajo_realizado': fields.boolean('Realizado'),
	}

bag_puestos_trabajo_work_done()


class bag_airline(osv.osv):
	_name = 'bag.airline'
	_description = 'Airline'

	_columns = {
		'name': fields.char('Airline', size=64, required=True),
		'code': fields.char('Codigo', size=2, required=True),
		'address': fields.char('Domicilio', size=64),
		'vat': fields.char('CUIT', size=15),
		'corporate_name': fields.char('Razon Social', size=64),
		'supplier': fields.char('Proveedor', size=64),
		'contract': fields.char('Contrato', size=64),
		'return_report': fields.boolean('Imprime Finiquito'),
		'pricelist' : fields.integer('Lista de precios'),
	}
bag_airline()

class bag_pricelist(osv.osv):
	_name = 'bag.pricelist'
	_description = 'Price List'

	_columns = {
		'name': fields.char('Orden de Compra', size=64, required=True),
		'airline_id': fields.many2one('bag.airline', 'Aerolinea', required=True),
		'date_start': fields.date('Fecha Desde', required=True),
		'date_end': fields.date('Fecha Hasta', required=True),
		'tope1': fields.float('Tope 1', digits=(12, 2)),
		'tope2': fields.float('Tope 2', digits=(12, 2)),
		'pricelist_lines': fields.one2many('bag.pricelist.line', 'pricelist_id', 'Precios', ondelete="cascade"),
		'pricelist_lines_envios': fields.one2many('bag.pricelist.line.envio', 'pricelist_id', 'Precios Envios'),
	}

	def create_lines(self, cr, uid, ids, context=None):
		repair_work_obj = self.pool.get('bag.work')
		for pl in self.browse(cr, uid, ids, context=context):
			works = repair_work_obj.browse(cr, uid, repair_work_obj.search(cr, uid, []))
			for work in works:
				self.pool.get('bag.pricelist.line').create(cr, uid, {
					'pricelist_id': pl.id,
					'work_id': work.id,
					'price': 0.0,
				})
		return True

	def create_lines_envios(self, cr, uid, ids, context=None):
		repair_envio_obj = self.pool.get('bag.sending')
		for pl in self.browse(cr, uid, ids, context=context):
			envios = repair_envio_obj.browse(cr, uid, repair_envio_obj.search(cr, uid, []))
			for envio in envios:
				self.pool.get('bag.pricelist.line.envio').create(cr, uid, {
					'pricelist_id': pl.id,
					'send_id': envio.id,
					'price': 0.0,
				})
		return True

bag_pricelist()

class bag_pricelist_line(osv.osv):
	_name = 'bag.pricelist.line'
	_description = 'Price List Line'

	_columns = {
		'pricelist_id': fields.many2one('bag.pricelist', 'Lista de Precios', required=True, ondelete="cascade"),
		'work_id': fields.many2one('bag.work', 'Trabajo', required=True),
		'price': fields.float('Precio', digits=(12, 2)),
	}

bag_pricelist_line()

class bag_pricelist_line_envio(osv.osv):
	_name = 'bag.pricelist.line.envio'
	_description = 'Price List Line Envio'

	_columns = {
		'pricelist_id': fields.many2one('bag.pricelist', 'Lista de Precios', required=True),
		'send_id': fields.many2one('bag.sending', 'Envio', required=True),
		'price': fields.float('Precio', digits=(12, 2)),
	}

bag_pricelist_line_envio()

class bag_scale(osv.osv):
	_name = 'bag.scale'
	_description = 'Scale'

	_columns = {
		'name': fields.char('Escala', size=32, required=True),
		'description': fields.char('Descripcion', size=32, required=True),
	}
bag_scale()

class bag_state(osv.osv):
	_name = 'bag.state'
	_description = 'State'

	_columns = {
		'name': fields.char('Estado', size=32, required=True),
		'code': fields.char('Codigo', size=3, required=True),
# 		'group': fields.many2many('res.groups','name','Grupos', required=True),
	}
bag_state()

class bag_shelving(osv.osv):
	_name = 'bag.shelving'
	_description = 'Shelving'

	_columns = {
		'name': fields.char('Estanteria', size=32, required=True),
		'code': fields.char('Codigo', size=3, required=True),
		'state_id': fields.many2one('bag.state', 'Estado'),
	}

	def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
		if not args:
			args = []
		if not context:
			context = {}
		if name:
			ids = self.search(cr, uid, [('code', '=', name)] + args, limit=limit, context=context)
			if not ids:
				ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
		else:
			ids = self.search(cr, uid, args, limit=limit, context=context)
		return self.name_get(cr, uid, ids, context)
bag_shelving()

class bag_sending(osv.osv):
	_name = 'bag.sending'
	_description = 'Sending'

	_columns = {
		'name': fields.char('Envio', size=32, required=True),
	}

bag_sending()

class bag_work_to_be_done(osv.osv):
	_name = 'bag.work_to_be_done'
	_description = 'Work to be done'

	_columns = {
		'name': fields.char('Name', size=24),
		'service_id': fields.many2one('bag.service', 'Repair'),
		'work_id': fields.many2one('bag.work', 'Work'),
		'quantity': fields.integer('Quantity'),
		'price': fields.float('Price', digits=(12, 2)),

	}

	_defaults = {
		'quantity': lambda *a: 1,
	}

	def onchange_work_id(self, cr, uid, ids, repair_date, work_id, airline_id, quantity):

		airline_obj = self.pool.get('bag.airline')
		work_obj = self.pool.get('bag.work')
		pricelist_obj = self.pool.get('bag.pricelist')

		if (not airline_id) or (not work_id):
			return {'value': {
						'price': False,
					}
			}
		airline = airline_obj.browse(cr, uid, airline_id)
		work = work_obj.browse(cr, uid, work_id)
		pricelist_ids = pricelist_obj.search(cr, uid, [('airline_id', '=', airline.id), ('date_start', '<=', repair_date), ('date_end', '>=', repair_date)])

		# print "pricelist_ids" + str(pricelist_ids)
		# print "airline" + str(airline.id)
		# print "repair.date" + str(repair_date)

		pricelist = pricelist_obj.browse(cr, uid, pricelist_ids[0])

		for line in pricelist.pricelist_lines:
			if line.work_id.id == work.id:
				if quantity == 1:
					price = line.price
				if quantity > 1:
					desc = 0.7
					price = line.price + (quantity - 1) * line.price * desc

		return {'value': {
					'price': price,
				}
		}
bag_work_to_be_done()

class bag_work(osv.osv):
	_name = 'bag.work'
	_description = 'Work'

	def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
		if not args:
			args = []
		if not context:
			context = {}
		if name:
			ids = self.search(cr, uid, [('code', '=', name)] + args, limit=limit, context=context)
			if not ids:
				ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
		else:
			ids = self.search(cr, uid, args, limit=limit, context=context)
		return self.name_get(cr, uid, ids, context)

	_columns = {
		'name': fields.char('Trabajo', size=32, required=True),
		'code': fields.char('Codigo', size=32, required=True),
		'without_discount': fields.boolean('Sin Descuento'),
		'price' : fields.float('Precio1', digits=(12, 2)),
		'price2' : fields.float('Precio2', digits=(12, 2)),
		'price3' : fields.float('Precio3', digits=(12, 2)),

	}
bag_work()

class bag_work_done(osv.osv):
	_name = 'bag.work_done'
	_description = 'Work done'

	_columns = {
		'name': fields.char('Name', size=24),
		'service_id': fields.many2one('bag.service', 'Repair'),
		'work_id': fields.many2one('bag.work', 'Work'),
		'quantity': fields.integer('Quantity'),
		'price': fields.float('Price', digits=(12, 2)),

	}
bag_work_done()

class bag_location(osv.osv):
	_name = 'bag.location'
	_description = 'Location'

	_columns = {
		'name': fields.char('Ubicacion', size=32, required=True),
	}

bag_location()

class bag_problemas(osv.osv):
	_name = 'bag.problemas'
	_description = 'Problemas'

	_columns = {
		'name': fields.char('Name', size=24),
		'service_id': fields.many2one('bag.service', 'Repair'),
		'fecha_volvio': fields.datetime('Fecha (Cuando Volvio)'),
		'como_volvio': fields.char('Como Volvio', size=64),
		'que_se_le_hizo': fields.char('Que se le hizo (Solucion)', size=64),
		'responsable': fields.many2one('res.users', 'Responsable Bag Service'),
		'responsable_aerolinea': fields.char('Responsable Aerolinea', size=64),
		'fecha_envio': fields.datetime('Fecha (Cuando Se Envio)'),
		'como_envio': fields.char('Como se Envio', size=64),
		'nueva_entrega': fields.date('Nueva Entrega'),
	}
bag_problemas()

class bag_llamados(osv.osv):
	_name = 'bag.llamados'
	_description = 'Llamados'

	_columns = {
		'name': fields.char('Name', size=24),
		'service_id': fields.many2one('bag.service', 'Repair'),
		'fecha': fields.datetime('Fecha'),
		'quien_llamo': fields.char('Quien Llamo', size=64),
		'detalle': fields.text('Detalle'),
		'quien_tomo': fields.many2one('res.users', 'Quien Tomo'),
		'acciones': fields.text('Acciones'), 	 }
bag_llamados()

class bag_state_samsonite(osv.osv):
	_name = 'bag.state.samsonite'
	_description = 'State Samsonite'

	_columns = {
		'name': fields.char('Estado', size=32, required=True),
	}
bag_state_samsonite()


class bag_product_samsonite(osv.osv):
	_name = 'bag.product.samsonite'
	_description = 'Product Samsonite'

	_columns = {
		'name': fields.char('SKU', size=32, required=True),
		'description': fields.char('Descripcion', size=64, required=True),
	}
bag_product_samsonite()

class bag_supplier(osv.osv):
	_name = 'bag.supplier'
	_description = 'Supplier'

	_columns = {
		'name': fields.char('Tercero', size=32, required=True),
	}
bag_supplier()

# Clase Principal Orden de Reparacion
class bag_service (osv.osv):
#---------
# Definicion de Funciones
#-----------


	def onchange_work_to_be_done(self, cr, uid, ids, work_to_be_done, airline_id, repair_date, discount, shipping_cost):
		work_obj = self.pool.get('bag.work')
		pricelist_obj = self.pool.get('bag.pricelist')				
				
		price = 0.0
		
		especial = False
		if discount == False or discount == None:
			discount = 0.0
			
		for work in work_to_be_done:
			try:
				if work[2]:  # chequeo que no sea "False" el trabajo
					if work[2]['work_id']:
			# 								print "work", work
						price += 	work[2]['price'] * work[2]['quantity']
						work = work_obj.browse(cr, uid, work[2]['work_id'])
						especial = especial or work.without_discount
			except Exception, args:
				print args
		pricelist_ids = pricelist_obj.search(cr, uid, [('airline_id', '=', airline_id), ('date_start', '<=', repair_date), ('date_end', '>=', repair_date)])
		
		if pricelist_ids:
			pricelist = pricelist_obj.browse(cr, uid, pricelist_ids[0])
# 			else:
# 				pricelist_ids = pricelist_obj.search(cr, uid, [('airline_id', '=', airline_id), ('date_start', '<=', repair_date), ('date_end', '>=', repair_date)])
# 				pricelist = pricelist_obj.browse(cr, uid, pricelist_ids[0])

		else:
			pricelist_ids = pricelist_obj.search(cr, uid, [('airline_id', '=', airline_id), ('date_start', '<=', repair_date), ('date_end', '>=', repair_date)])
			if pricelist_ids:
				pricelist = pricelist_obj.browse(cr, uid, pricelist_ids[0])
			else:
				mensaje = 'No se encontro una lista de precios.'
				raise osv.except_osv(('Error al agregar trabajo') , mensaje)
		if not especial:
			tope = pricelist.tope1
		else: 
			tope = pricelist.tope2
		if price > tope:
			price = tope

		#calculo del precio segun valores anteriores cargados###
		price_ant = 0
		if ids and ids[0]:
			repair = self.browse(cr, uid, ids[0], context={})			
			for wtbd in repair.work_to_be_done:
				price_ant += wtbd.price * wtbd.quantity
		
		########################################################	

		price = (price_ant + price) * (1 + IVA_VALUE)  # subtotal.
		total_price = price * (1 - discount / 100) + shipping_cost  # con el descuento.		
					
		return {'value': 
							{
								'estimated_price': price,
								'price_buffer': total_price,
# 										'balance':balance,
							}
						}


	def create(self, cr, uid, vals, context={}):
		
		seq_id = self.pool.get('ir.sequence').search(cr, uid, [('name', '=', 'Orden de Reparacion')])[0]  # put whatever name you have
# 		  seq_number = self.pool.get('ir.sequence').get_id(cr, uid, seq_id, 'id=%s')
		seq_number = self.pool.get('ir.sequence').get(cr, uid, 'bag.service')
		vals['name'] = seq_number
		vals['date'] = time.strftime('%Y-%m-%d')
		
		discount = 0.00
		if 'base_discount' in vals.keys():
			discount = vals['base_discount']
			
		if 'work_to_be_done' in vals.keys():
			onchange_result = self.onchange_work_to_be_done(cr, uid, [], vals['work_to_be_done'], vals['airline_id'], vals['date'], discount, vals['shipping_cost'])
			vals['estimated_price'] = onchange_result['value']['estimated_price']
			vals['price_buffer'] = onchange_result['value']['price_buffer']
			vals['balance'] = vals['price_buffer']
		
		return super(bag_service, self).create(cr, uid, vals, context)

	def write(self, cr, uid, ids, vals, context={}):
 		price_ant = 0
 		balance = 0
		super(bag_service, self).write(cr, uid, ids, vals, context)
		#recalculo del precio ###
		if ids[0]:
			repair = self.browse(cr, uid, ids[0], context={})
			
			for wtbd in repair.work_to_be_done:
				price_ant += wtbd.price * wtbd.quantity
 		
		########################################################	
 
			price_ant = price_ant * (1 + IVA_VALUE)  # subtotal.
			total_price = price_ant * (1 - repair.base_discount / 100) + repair.shipping_cost  # con el descuento.
 			balance = total_price - repair.total_payments
		return super(bag_service, self).write(cr, uid, ids, {'estimated_price':price_ant, 'price_buffer':total_price, 'balance':balance})
	
	def copy(self, cr, uid, id, default=None, context=None):
				if not default:
						default = {}
				default.update({
						'state':'draft',
						'repaired':False,
						'invoiced':False,
						'invoice_id': False,
						'picking_id': False,
				})
				return super(bag_service, self).copy(cr, uid, id, default, context)
	
	def _check_balance_before_close(self, cr, uid, ids, context=None):
		
		record = self.browse(cr, uid, ids, context=context)
		state_obj = self.pool.get('bag.state')
		
		res = state_obj.read(cr, uid, ids, ['name', 'id'])
		
		for data in record:
			if data.type == 'particular':
				
				if data.state_id.name == 'Entregado' and data.balance > 0.00:
					print "Balance Positivo"
					return False
				else:
					print "Balance Negativo"
					return True
			else:
				print 'No es particular'
				return True
			
		print 'Sale del loop'
		return True
	
	def _check_balance_before_save(self, cr, uid, ids, context=None):

		record = self.browse(cr, uid, ids, context=context)
		
		for repair in self.browse(cr, uid, ids, context=context):
# 			print "Precio, seña y precio estimado",repair.price,repair.prepayment,repair.estimated_price
			if repair.price:
				importe_total = repair.price
				if importe_total > 0.00:
					work_payments = self.pool.get('bag.work_payments')
					balance = importe_total
					for num_id in ids:
						wp_ids = work_payments.search(cr, uid, [('service_id', '=', num_id)])
						for wp_id in wp_ids:
							try:
								wp = work_payments.browse(cr, uid, wp_id)
								balance -= wp.amount
							except IndexError:
								# si es una nueva, nos tira este error.
								return True
					if balance < 0.00:
						return False
						
			else:
				return True
# 		for data in record:
# 			if data.balance!=False:
# 				print "Balance dejuan pablo: ",data.balance
# 				if data.balance<0:
# 					print "No se puede guardar, tiene saldo negativo"
# 					return False
# 				else:
# 					return True
		return True

	def _get_total_sena(self, cr, uid, ids, field_name, arg, context):
		res = {}
		
		for repair in self.browse(cr, uid, ids, context=context):
			sena = 0
			work_payments = self.pool.get('bag.work_payments')
			for num_id in ids:
				wp_ids = work_payments.search(cr, uid, [('service_id', '=', num_id)])
				for wp_id in wp_ids:
					try:
						wp = work_payments.browse(cr, uid, wp_id)
						if wp.payment_type == 'prepayment':
							sena += wp.amount
					except IndexError:
						# si es una nueva, nos tira este error.
						return
			res[repair.id] = sena
		return res
		

	def _get_total_price(self, cr, uid, ids, field_name, arg, context):
		res = {}
		for repair in self.browse(cr, uid, ids, context=context):
# 			print "Precio, seña y precio estimado",repair.price,repair.prepayment,repair.estimated_price
			price = 0
			for wtbd in repair.work_to_be_done:
				price += wtbd.price
			
			res[repair.id] = price * (1 + IVA_VALUE) * (1 - repair.base_discount / 100.00) + repair.shipping_cost
			
		return res

	def onchange_work_payments(self, cr, uid, ids, payments, total_price):
		
# 		rep_obj = self.pool.get('bag.service')
# # 		rep_id=rep_obj.search(cr,uid,[])
# # 		print rep_id
# # 		work_done_obj.write(cr, uid, work_ids[0], {'quantity':quantity, 'price':price})   
# 		total_income = 0.0
# 		for pay in payments:
# 			try:
# 				if pay[2]['amount'] != False:
# 					total_income += float(pay[2]['amount'])
# 			except TypeError, arg:
# 				print arg
# 				continue
# 			
# 		balance = total_price - total_income
# # 		self.write(cr, uid, ids, {'balance':balance})
# 		return {'value': {
# 			'total_payments': total_income,
# 			'price_buffer' : total_income
# 			# 'balance': balance,
# 			}
		return True
# 		}	

	def _calculate_balance(self, cr, uid, ids, field_name, arg, context):
		res = {}
		
# 		work_obj = self.pool.get('repair.work')
		for repair in self.browse(cr, uid, ids, context=context):
# 	   		 print "Precio, seña y precio estimado",repair.price,repair.prepayment,repair.estimated_price
			price = 0.00
			for wtbd in repair.work_to_be_done:
				price += wtbd.price
			
			if price:
				res[repair.id] = price * (1 + IVA_VALUE) * (1 - repair.base_discount / 100.00) + repair.shipping_cost
				if res[repair.id] > 0:
					work_payments = self.pool.get('bag.work_payments')
						
					for num_id in ids:
						wp_ids = work_payments.search(cr, uid, [('service_id', '=', num_id)])
						for wp_id in wp_ids:
							try:
								wp = work_payments.browse(cr, uid, wp_id)
								res[repair.id] -= wp.amount
							except IndexError:
								# si es una nueva, nos tira este error.
								return
				
					# else:
					# 	res[repair.id] = 0.00	  
		
			return res

	def onchange_envio_id(self, cr, uid, ids, send_id, airline_id, date, discount, context=None):
		pricelist_obj = self.pool.get('bag.pricelist')
		if (not airline_id):
			return {'value': {
		  	'shipping_cost': False,
			}
		}
		pricelist_ids = pricelist_obj.search(cr, uid, [('airline_id', '=', airline_id), ('date_start', '<=', date), ('date_end', '>=', date)])
		if not pricelist_ids:
			mensaje = 'No se encontro una lista de precios.'
			raise osv.except_osv(('Mensaje') , mensaje)

		pricelist = pricelist_obj.browse(cr, uid, pricelist_ids[0])
		price = 0.0
		for line in pricelist.pricelist_lines_envios:
			if line.send_id.id == send_id:
				price = line.price
				repair_obj = self.pool.get('bag.service')

		for obj in repair_obj.browse(cr, uid, ids):
			if obj.estimated_price:
				return {'value': {
								'shipping_cost': price,
								'price_buffer': (obj.estimated_price * (1 - discount / 100) + price)
				}
			}
		return {'value': {'shipping_cost': price, }
	}

	def onchange_partner_id(self, cr, uid, ids, part):
		part_obj = self.pool.get('res.partner')
		if not part:
			return {'value': {
					'address_str': "",
					'address_num_str': "",
					'piso_dpto_str': "",
					'phone_str': "",
					'zone_str': "",
					}
			  }
		else:
		  	partner = part_obj.browse(cr, uid, part)
	  	if not partner.street:
			partner_street = str(partner.street2)
	  	else:
			partner_street = str(partner.street)
			partner_num = str(partner.street_num)
		if not partner.piso_dpto:
			partner_piso_dpto = ""
		else:
			partner_piso_dpto = str(partner.piso_dpto)

		# phone_str = None		 	
		# if partner.mobile and partner.phone:
		# 	phone_str = partner.phone + " / " + partner.mobile 	 
		# else:
		# 	if partner.phone:
		# 		phone_str = str(partner.phone)
		# 	if partner.mobile:
		# 		phone_str = str(partner.mobile)
		if partner.zona:
			partner_zona = str(partner.zona)
		else:
			partner_zona = ""
		return {'value': {'address_str': partner_street,
						'address_num_str': partner_num,
						'piso_dpto_str': partner_piso_dpto,
						'phone_str': partner.phone_str,
						'zone_str':partner_zona, }}

	def onchange_type(self, cr, uid, ids, type, context=None):
		if type == 'particular':
			return {'value': {'airline_id': 19, }}
		else:
			return {'value': {'airline_id': False, }}

	def onchange_base_discount(self, cr, uid, ids, discount, est_price, shipping_cost, context=None):
	# si la orden es nueva, est_price y total_payments, pueden ser False
		if not est_price:
			est_price = 0.0
			valid_discount = 0.0
			old_discount = 0.0
		if discount < 0:
			valid_discount = 0
		elif discount > 100:
			valid_discount = 100
		else:
			valid_discount = discount
			total_price = est_price * (1 - valid_discount / 100.00) + shipping_cost
		return {'value': {
						'base_discount': valid_discount,
						'price_buffer':total_price,
# 		'balance':balance,
				}
			}

	def _estado_defecto(self, cr, uid, context=None):
		estado = self.pool.get('bag.state').search(cr, uid, [('name', '=', 'Recibido')])
		return estado

	_name = 'bag.service'
	_description = 'Service Order'
	_columns = {
		'name': fields.char('Numero Orden', size=24),
		'type': fields.selection([('particular', 'Particular'), ('airline', 'Aerolinea')], 'Type', required=True),
		'date': fields.date('Fecha', required=True),
		'date_promised': fields.date('Fecha Prometida', required=True),
		'partner_id' : fields.many2one('res.partner', 'Cliente'),
		'address_str': fields.related('partner_id', 'street', type='char', size='128'),
		'address_num_str': fields.related('partner_id', 'street_num', type='char'),
		'piso_dpto_str': fields.related('partner_id', 'piso_dpto', type='char', size='128'),
		'phone_str': fields.related('partner_id', 'phone_str', type='char', size='128'),
		'zone_str': fields.related('partner_id', 'street', type='char'),
		'type_id': fields.many2one('bag.type', 'Tipo'),
		'format_id': fields.many2one('bag.format', 'Formato'),
		'color_id': fields.many2one('bag.color', 'Color'),
		'material_id': fields.many2one('bag.material', 'Material'),
		'size_id': fields.many2one('bag.size', 'Tamano'),
		'description': fields.char('Descripcion', size=64),
		'brand': fields.char('Marca', size=64),
		'model': fields.char('Modelo', size=64),
		'airline_id': fields.many2one('bag.airline', 'Aerolinea', required=True),
		'branch': fields.char('Sucursal', size=32),
		'scale_id': fields.many2one('bag.scale', 'Escala'),
		'incoming_guide': fields.char('Guia Entrante', size=32),
		'case_number': fields.char('Numero Caso', size=32),
		'outgoing_guide': fields.char('Guia Saliente', size=32),
		'internal_notes': fields.text('Nota'),
		'estimated_price': fields.float('Costo Estimado', digits=(12, 2)),
		'price_buffer': fields.float('Buffer Importe', digits=(12, 2)),
		'base_discount': fields.float('Descuento', digits=(4, 2)),
		#'prepayment': fields.function(_get_total_sena, string='Sena', store=True, readonly=True),
		'prepayment': fields.float(digits=(12,2)),
		'shipping_cost': fields.float('Costo Envio', digits=(12, 2)),
		'action': fields.selection([('reparar', 'Reparar'), ('reemplazar', 'Reemplazar')], 'Action', required=True),
		'user_id': fields.many2one('res.users', 'Usuario'),
		'state_id': fields.many2one('bag.state', 'Estado', required=True),
		'shelving_id': fields.many2one('bag.shelving', 'Estanteria'),
		'urgent': fields.boolean('Urgente'),
		'papers': fields.boolean('Papeles'),
		'attention': fields.boolean('Atencion'),
		'monitoring': fields.boolean('Seguimiento'),
		'send': fields.boolean('Enviar'),
		'send_id': fields.many2one('bag.sending', 'Envio'),
		'taxi': fields.boolean('Remisero'),
		'baby_carriage': fields.boolean('Coche BB'),
		'date_return': fields.date('Fecha Entregado'),
		'work_to_be_done': fields.one2many('bag.work_to_be_done', 'service_id', 'Trabajo a realizar'),
		'quotation_notes': fields.text('Observaciones de las Tareas'),  # Tarea Observacion
		'work_done': fields.one2many('bag.work_done', 'service_id', 'Trabajo realizado'),
		'location_id': fields.many2one('bag.location', 'Ubicacion Actual'),
		'retires_location_id': fields.many2one('bag.location', 'Retira en'),
		'work_made': fields.text('Nota en Reparacion'),  # Trabajo Realizado
		'repaired_by_id': fields.many2one('res.users', 'Reparado por'),
		'labor_price': fields.float('Mano de Obra', digits=(12, 2)),
		'materials_price': fields.float('Materiales', digits=(12, 2)),
		'price': fields.float('Importe', digits=(12, 2)),
		'free': fields.boolean('Sin cargo'),
		'summary_number': fields.char('Nro. Resumen', size=32),
		'route_sheet_number': fields.char('Nro. Hoja de Ruta', size=32),
		'invoice_number': fields.char('Nro. Factura', size=32),
		'marca_resumen': fields.boolean('Marca Resumen'),
		'marca_hoja_ruta': fields.boolean('Marca Hoja Ruta'),
		'web_password': fields.char('Web Password', size=6, readonly=True),
		'incoming_type': fields.selection([('cliente', 'Trajo el cliente'), ('remisero', 'Trajo un Remisero'), ('buscar', 'Se paso a buscar')], 'Tipo Ingreso'),
		'persona_retiro': fields.char('Persona Retiro', size=64),
		'lugar_retiro': fields.char('Lugar Retiro', size=64),
		'fecha_retiro': fields.date('Fecha Retiro'),
		'costo_adicional_retiro': fields.float('Costo Adicional', digits=(12, 2)),
		'outgoing_type': fields.selection([('cliente', 'Vino a buscar el cliente'), ('remisero', 'Vino a buscar un Remisero'), ('domicilio', 'Se envio a domicilio')], 'Tipo Egreso'),
		'persona_llevo': fields.char('Persona Llevo', size=64),
		'lugar_llevo': fields.char('Lugar Llevo', size=64),
		'fecha_llevo': fields.date('Fecha Llevo'),
		'costo_adicional_llevo': fields.float('Costo Adicional', digits=(12, 2)),
		'autorizo_quien': fields.char('Quien Autorizo', size=64),
		'autorizo_medio': fields.selection([('mail', 'Mail'), ('fax', 'Fax'), ('tel', 'Tel')], 'Por que medio'),
		'autorizo_fecha': fields.date('Fecha Autorizacion'),
		'autorizo_que': fields.char('Que se Autorizo', size=64),
		'autorizo_solicito_id': fields.many2one('res.users', 'Quien Solicito'),
		'autorizo_avisa_id': fields.many2one('res.users', 'A quien se le Avisa'),
		'problemas': fields.one2many('bag.problemas', 'service_id', 'Problemas'),
		'llamados': fields.one2many('bag.llamados', 'service_id', 'Llamados'),
		'samsonite_nroremito': fields.char('Nro Remito', size=32),
		'samsonite_nrointerno': fields.char('Nro Interno', size=32),
		'samsonite_state_id': fields.many2one('bag.state.samsonite', 'Estado Samsonite'),
		'samsonite_producto_id': fields.many2one('bag.product.samsonite', 'Producto Samsonite'),
		'samsonite_lugarcompra': fields.char('Lugar Compra', size=32),
		'samsonite_nrofactura': fields.char('Nro Factura', size=32),
		'samsonite_fechacompra': fields.date('Fecha Compra'),
		'samsonite_presupuestado': fields.boolean('Presupuestado'),
		'modificaciones_detalle': fields.text('Modificaciones Detalle'),
		'invoiced': fields.boolean('Facturado'),
		'date_repair_supplier': fields.date('Fecha Repara 3ro.'),
		'repair_supplier_id': fields.many2one('bag.supplier', 'Nombre Tercero'),
		'payments': fields.one2many('bag.work_payments', 'service_id', 'Pagos y Saldo'),
		#'balance': fields.function(_calculate_balance, method=True, string='Calculo Saldo', store=True),
		'balance': fields.float(digits=(12,2)),
		'total_payments': fields.float('Total Pagos', digits=(12, 2)),
  		}
	_defaults = {
                 'date': lambda *a: time.strftime('%Y-%m-%d'),
                 'state_id': _estado_defecto,
                 'web_password': lambda *a: ''.join(random.choice(string.digits) for x in range(6)),
                 'action': lambda *a: 'reparar',
                 }
	_constraints = [(_check_balance_before_close, '\nError: No se puede entregar, tiene saldo positivo', ['state_id']),
					(_check_balance_before_save, '\nError: No se puede guardar, la suma de pagos supera el Importe Total', ['balance']), ]
	_order = "date desc, name desc"

bag_service()


class bag_work_payments(osv.osv):
	_name = 'bag.work_payments'
	_description = 'Payments and Balance'
	
	
	def onchange_service_id(self, cr, uid, ids, service_id, context={}):
		importe_total = 0
		if service_id:
			orden_obj = self.pool.get('bag.service').browse(cr, uid, service_id)
			importe_total = orden_obj.price_buffer - orden_obj.total_payments
			if importe_total <= 0:
				
				mensaje = 'La Orden de Reparación Nro:%s fue cancelada en su totalidad.' % orden_obj.name
				raise osv.except_osv(('Error al actualizar el importe de la Reparacion') , mensaje)
		else:
			importe_total = 0
		return {	
				'value': {'importe_total' : importe_total}
				}
		

	
	def create(self, cr, uid, vals, context={}):
		orden_obj = self.pool.get('bag.service').browse(cr, uid, vals['service_id'])
		vals_write = {}
		vals_write['total_payments'] = vals['amount'] + orden_obj.total_payments
		vals_write['prepayment'] = vals_write['total_payments']
		vals_write['balance'] = orden_obj.price_buffer - vals_write['total_payments']
#		if vals['payment_date'] > time.strftime('%Y-%m-%d'):
#			mensaje = 'No puede guardar una fecha mayor al dia de hoy. Por favor corrija'
#			raise osv.except_osv(('Error al cargar fecha de pago') , mensaje)
		vals['payment_date'] = time.strftime('%Y-%m-%d')
		# Si la orden ya esta cancelada, no puede guardar
		saldo = orden_obj.price_buffer - orden_obj.total_payments
		if saldo <= 0:
				mensaje = 'La Orden de Reparación Nro:%s fue cancelada en su totalidad.' % orden_obj.name
				raise osv.except_osv(('Error al actualizar el importe de la Reparacion') , mensaje)
		# No puede guardar montos negativos
		if vals['amount'] <= 0:
			mensaje = 'No puede guardar montos menores a cero. Por favor corrija' 
			raise osv.except_osv(('Error al actualizar el importe de la Reparacion') , mensaje)
		# Si el total de pagos es menor o igual a el importe total, escribe el nuevo pago y actualiza los saldos, sino tira mensaje de error
		if vals_write['total_payments'] <= orden_obj.price_buffer:
			self.pool.get('bag.service').write(cr, uid, [vals['service_id']], vals_write)
			create_id = super(bag_work_payments, self).create(cr, uid, vals, context)
			return create_id
		else:
			mensaje = 'El monto ingresado excede el saldo total de la Orden de Reparacion. Por favor corrija' 
			raise osv.except_osv(('Error al actualizar el importe de la Reparacion') , mensaje)
	
	def onchange_amount(self, cr, uid, ids, service_id, amount, importe_total, context={}):
		if service_id and importe_total:
			orden_obj = self.pool.get('bag.service').browse(cr, uid, service_id)
			if amount <= importe_total and importe_total != 0:
				importe_total = importe_total - amount
			else:
				mensaje = 'El monto excede el importe total de $%s. Por favor corrija' % importe_total
				raise osv.except_osv(('Error al actualizar el importe de la Reparacion') , mensaje)
		return {	
				'value': {'importe_total' : importe_total},
				}
				
	def _check_invoice_number(self, cr, uid, ids, context=None):
		record = self.browse(cr, uid, ids, context=context)
		for data in record:
			print data.invoice_number
			if data.invoice_number != False:
				if FACTURA_REX.match(data.invoice_number):
					return True
				else:
					return False
		return True
	
		
	_columns = {
		'payment_date': fields.date(' Date of Payment', required=True),
		'service_id': fields.many2one('bag.service', 'Repair'),
		'invoice_number': fields.char('Invoice Num.', size=11, required=True),
		'amount': fields.float('Amount', digits=(12, 2)),
		'importe_total' : fields.float('Saldo', digits=(12, 2)),
		'method': fields.selection((('cash', 'Efectivo'),
								('credit', 'T. Credito'),
								('debit', 'T. Debito')), "Metodo de Pago"),
		'cupon_number': fields.char('Coupon Num.', size=15),
		'payment_type': fields.selection((('prepayment', 'Seña'),
										('final', 'Saldo Final')),
										"Tipo de Operacion", required=True),
		}
	_defaults = {
	 			 'payment_date': lambda *a: time.strftime('%Y-%m-%d'),
 				 }
	_constraints = [(_check_invoice_number, '\nError: Revisar el numero de facturacion\n Debe estar en el rango 0000A000000 a 9999Z999999', ['invoice_number']), ]
				
bag_work_payments()
