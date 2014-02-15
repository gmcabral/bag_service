# -*- coding: utf-8 -*-
from osv import fields, osv, orm
import time
import decimal_precision as dp

class repair_cambiar_estado_caja(osv.osv_memory):
    _name='bag.cambiar_estado_caja'
    _description='Cambiar Estado Caja'
    _columns = {
                'state_id': fields.many2one('bag.state','Estado',required=True,
                                domain="['|',('code','=','T'),('code','=','AD')]"),
                }
    def cambiar_estado(self, cr, uid, ids, context=None):
        data  = self.browse(cr, uid, ids)[0]
        
        order_obj = self.pool.get('bag.service')
        active_ids = context and context.get('active_ids',[])
        if order_obj.browse(cr, uid, active_ids)[0].modificaciones_detalle:
            detalle = order_obj.browse(cr, uid, active_ids)[0].modificaciones_detalle
        else:
            detalle = ""
        detalle = detalle + '\n\nUsuario: %s\n' % (self.pool.get('res.users').browse(cr, uid, uid).name) + 'Cambio de Estado: ' + time.strftime('%d/%m/%Y %H:%M:%S') + ' a '+ data.state_id.name

        order_obj.write(cr, uid, active_ids, {'state_id':data.state_id.id,'date_return':time.strftime('%Y-%m-%d'),'modificaciones_detalle': detalle})
        return {
                'type': 'ir.actions.act_window_close',
         }
    
repair_cambiar_estado_caja()

class repair_cambiar_estado_logistica(osv.osv_memory):
    _name='bag.cambiar_estado_logistica'
    _description='Cambiar Estado Logistica'
    _columns = {
                'state_id': fields.many2one('bag.state','Estado',required=True,
                                domain="['|','|','|','|','|','|','|','|','|',"\
                                "('code','=','O'),('code','=','AD'),('code','=','Y'),"\
                                "('code','=','CC'),('code','=','12'),"\
                                "('code','=','R'),('code','=','V'),"\
                                "('code','=','B'),('code','=','M'),"\
                                "('code','=','X')]"),
                }
    def cambiar_estado(self, cr, uid, ids, context=None):
        data  = self.browse(cr, uid, ids)[0]
        
        order_obj = self.pool.get('bag.service')
        active_ids = context and context.get('active_ids',[])
        if order_obj.browse(cr, uid, active_ids)[0].modificaciones_detalle:
            detalle = order_obj.browse(cr, uid, active_ids)[0].modificaciones_detalle
        else:
            detalle = ""
        detalle = detalle + '\n\nUsuario: %s\n' % (self.pool.get('res.users').browse(cr, uid, uid).name) + 'Cambio de Estado: ' + time.strftime('%d/%m/%Y %H:%M:%S') + ' a '+ data.state_id.name

        order_obj.write(cr, uid, active_ids, {'state_id':data.state_id.id,'modificaciones_detalle': detalle})
        return {
                'type': 'ir.actions.act_window_close',
         }
    
repair_cambiar_estado_logistica()
class repair_cambiar_estado_mostrador(osv.osv_memory):
    _name='bag.cambiar_estado_mostrador'
    _description='Cambiar Estado Mostrador'
    _columns = {
                'state_id': fields.many2one('bag.state','Estado',required=True,
                                domain="['|','|','|','|','|',"\
                                "('code','=','O'),('code','=','Y')"\
                                ",('code','=','AD'),('code','=','CC')"\
                                ",('code','=','12'),('code','=','R')]"),
                }
    def cambiar_estado(self, cr, uid, ids, context=None):
        data  = self.browse(cr, uid, ids)[0]
        
        order_obj = self.pool.get('bag.service')
        active_ids = context and context.get('active_ids',[])
        if order_obj.browse(cr, uid, active_ids)[0].modificaciones_detalle:
            detalle = order_obj.browse(cr, uid, active_ids)[0].modificaciones_detalle
        else:
            detalle = ""
            
        detalle = detalle + '\n\nUsuario: %s\n' % (self.pool.get('res.users').browse(cr, uid, uid).name) + 'Cambio de Estado: ' + time.strftime('%d/%m/%Y %H:%M:%S') + ' a '+ data.state_id.name

        order_obj.write(cr, uid, active_ids, {'state_id':data.state_id.id,'modificaciones_detalle': detalle})
        return {
                'type': 'ir.actions.act_window_close',
         }
    
repair_cambiar_estado_mostrador()
class repair_cambiar_estado_facturacion(osv.osv_memory):
    _name='bag.cambiar_estado_facturacion'
    _description='Cambiar Estado Facturacion'
    _columns = {
                'state_id': fields.many2one('bag.state','Estado',required=True,
                                domain="['|','|','|','|','|','|','|',"\
                                "('code','=','O'),('code','=','V'),"\
                                "('code','=','B'),('code','=','D'),"\
                                "('code','=','Z'),('code','=','S'),"\
                                "('code','=','L'),('code','=','N')]"),
                }
    def cambiar_estado(self, cr, uid, ids, context=None):
        data  = self.browse(cr, uid, ids)[0]
        
        order_obj = self.pool.get('bag.service')
        active_ids = context and context.get('active_ids',[])
        if order_obj.browse(cr, uid, active_ids)[0].modificaciones_detalle:
            detalle = order_obj.browse(cr, uid, active_ids)[0].modificaciones_detalle
        else:
            detalle = ""
        detalle = detalle + '\n\nUsuario: %s\n' % (self.pool.get('res.users').browse(cr, uid, uid).name) + 'Cambio de Estado: ' + time.strftime('%d/%m/%Y %H:%M:%S') + ' a '+ data.state_id.name

        order_obj.write(cr, uid, active_ids, {'state_id':data.state_id.id,'modificaciones_detalle': detalle})
        return {
                'type': 'ir.actions.act_window_close',
         }
    
repair_cambiar_estado_facturacion()

class repair_cambiar_estado_at_cliente(osv.osv_memory):
    _name='bag.cambiar_estado_at_cliente'
    _description='Cambiar Estado At Cliente'
#    domain="[('code','=','V'),"\
#                                "('code','=','B'),('code','=','D'),"\
#                                "('code','=','Z'),('code','=','S'),"\
#                                "('code','=','L')]"
    _columns = {
                'state_id': fields.many2one('bag.state','Estado',required=True,
                                domain="['|','|','|','|','|',('code','=','V'),"\
                                "('code','=','B'),('code','=','D'),"\
                                "('code','=','Z'),('code','=','S'),"\
                                "('code','=','L')]"),
                }
    def cambiar_estado(self, cr, uid, ids, context=None):
        data  = self.browse(cr, uid, ids)[0]
        
        order_obj = self.pool.get('bag.service')
        active_ids = context and context.get('active_ids',[])
        if order_obj.browse(cr, uid, active_ids)[0].modificaciones_detalle:
            detalle = order_obj.browse(cr, uid, active_ids)[0].modificaciones_detalle
        else:
            detalle = ""
        detalle = detalle + '\n\nUsuario: %s\n' % (self.pool.get('res.users').browse(cr, uid, uid).name) + 'Cambio de Estado: ' + time.strftime('%d/%m/%Y %H:%M:%S') + ' a '+ data.state_id.name
        
        order_obj.write(cr, uid, active_ids, {'state_id':data.state_id.id,'modificaciones_detalle': detalle})
        return {
                'type': 'ir.actions.act_window_close',
         }
    
repair_cambiar_estado_at_cliente()