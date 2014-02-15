# -*- coding: utf-8 -*-
from osv import fields, osv, orm
import time
import decimal_precision as dp

class wizard_estanteria_individual(osv.osv_memory):
    _name = 'bag.estanteria_individual'
    _description = 'Modificacion Estanteria'

    _columns = {
        'service_id': fields.many2one('bag.service', 'Orden de Reparacion'),
        'shelving_id': fields.many2one('bag.shelving', 'Estanteria'), 
    }
    
    def trabajo_realizado(self, cr, uid, ids, context=None):
#        print "trabajo realizado"
        
        data  = self.browse(cr, uid, ids)[0]
        
#        print "ids", ids
#        print "data", data
                
        order_obj = self.pool.get('bag.service')
                    
        if data.service_id.modificaciones_detalle:
            detalle = data.service_id.modificaciones_detalle
        else:
            detalle = ""
            
        detalle = detalle + \
                    '\n\nUsuario: %s\n'%(self.pool.get('res.users').browse(cr, uid, uid).name)+ \
                    'Cambio de Estanteria:  ' + time.strftime('%d/%m/%Y %H:%M:%S') \
                    + ' a ' + data.shelving_id.name + '\nCambio de Estado:  '     \
                    + time.strftime('%d/%m/%Y %H:%M:%S') + ' a ' \
                    + data.shelving_id.state_id.name
        
        order_obj.write(cr, uid, [data.service_id.id], {'modificaciones_detalle': detalle, 'shelving_id': data.shelving_id.id, 'state_id': data.shelving_id.state_id.id})
                    
                
        return {
                'type': 'ir.actions.act_window_close',
         }

wizard_estanteria_individual()


class wizard_estanteria_grupal(osv.osv_memory):
    _name = 'bag.estanteria_grupal'
    _description = 'Modificacion Estanteria'

    _columns = {
        'service_ids': fields.one2many('bag.estanteria_grupal_repair_ids', 'estanteria_grupal_id', 'Ordenes Reparacion'),                               
        'shelving_id': fields.many2one('bag.shelving', 'Estanteria'), 
    }
    
    def trabajo_realizado(self, cr, uid, ids, context=None):
#        print "trabajo realizado"
        
        data  = self.browse(cr, uid, ids)[0]
        
#        print "ids", ids
#        print "data", data
                
        order_obj = self.pool.get('bag.service')
                    
        for repair in data.service_ids:
                    
            if repair.service_id.modificaciones_detalle:
                detalle = repair.service_id.modificaciones_detalle
            else:
                detalle = ""
                
            detalle = detalle + '\n\nUsuario: %s\n'%(self.pool.get('res.users').browse(cr, uid, uid).name) + 'Cambio de Estanteria:  ' + time.strftime('%d/%m/%Y %H:%M:%S') + ' a ' + data.shelving_id.name + '\nCambio de Estado:  '     + time.strftime('%d/%m/%Y %H:%M:%S') + ' a ' + data.shelving_id.state_id.name
            
            order_obj.write(cr, uid, [repair.service_id.id], {'modificaciones_detalle': detalle, 'shelving_id': data.shelving_id.id, 'state_id': data.shelving_id.state_id.id})
                    
                
        return {
                'type': 'ir.actions.act_window_close',
         }

wizard_estanteria_grupal()


class wizard_estanteria_grupal_repair_ids(osv.osv_memory):
    _name = 'bag.estanteria_grupal_repair_ids'

    _columns = {
        'service_id': fields.many2one('bag.service', 'Orden de Reparacion'),    
        'estanteria_grupal_id': fields.many2one('bag.estanteria_grupal', 'Grupal'),                         
    }

wizard_estanteria_grupal_repair_ids()