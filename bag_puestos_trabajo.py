# -*- coding: utf-8 -*-
from osv import fields, osv, orm
import time
import decimal_precision as dp

class wizard_puestos_trabajo(osv.osv):
    _name = 'repair.puestos_trabajo'
    _description = 'Puestos de Trabajo'

    _columns = {
        'repair_id': fields.many2one('repair', 'Orden de Reparacion',readonly=True, states={'draft':[('readonly',False)]}),
        'shelving_id': fields.many2one('repair.shelving', 'Puesto',readonly=True, states={'draft':[('readonly',False)]}), 
        'work_done': fields.one2many('repair.puestos_trabajo_work_done', 'puestostrabajo_id', 'Trabajo realizado',readonly=True, states={'draft':[('readonly',False)]}),                               
        'work_made': fields.text('Nota en Reparacion',readonly=True, states={'draft':[('readonly',False)]}),  
        'state': fields.selection([
            ('draft','Borrador'),
            ('confirmed','Confirmado'),
            ], 'Estado', readonly=True),
    }

    _defaults = {
        'state': lambda *a: 'draft',
    }
    
    def trabajo_realizado(self, cr, uid, ids, context=None):
        print "trabajo realizado"
        
        data  = self.browse(cr, uid, ids)[0]
#        
#        print "ids", ids
#        print "data", data
                
        order_obj = self.pool.get('repair')
        work_done_obj = self.pool.get('repair.work_done')
                    
        if data.repair_id.modificaciones_detalle:
            detalle = data.repair_id.modificaciones_detalle
        else:
            detalle = ""
            
        detalle = detalle +'\n\nUsuario: %s\n'%(self.pool.get('res.users').browse(cr, uid, uid).name) + 'Cambio de Estanteria:  ' + time.strftime('%d/%m/%Y %H:%M:%S') + ' a ' + data.shelving_id.name + '\nCambio de Estado:  '     + time.strftime('%d/%m/%Y %H:%M:%S') + ' a ' + data.shelving_id.state_id.name
        
        order_obj.write(cr, uid, [data.repair_id.id], {'modificaciones_detalle': detalle, 'shelving_id': data.shelving_id.id, 'state_id': data.shelving_id.state_id.id, 'work_made': data.work_made})
                    
        airline_obj = self.pool.get('repair.airline')
        airline = airline_obj.browse(cr, uid, data.repair_id.airline_id.id)

        work_obj = self.pool.get('repair.work')        
                    
        for line in data.work_done:               
            
            work_ids = work_done_obj.search(cr, uid, [('repair_id', '=', data.repair_id.id), ('work_id', '=', line.work_id.id)])     
                
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

                vals = {'repair_id': data.repair_id.id, 'work_id': line.work_id.id, 'quantity': 1, 'price': price}
                work_done_obj.create(cr, uid, vals)     
                
        return True

wizard_puestos_trabajo()


class wizard_puestos_trabajo_work_done(osv.osv):
    _name = 'repair.puestos_trabajo_work_done'
    _description = 'Puestos de Trabajo Work Done'

    _columns = {
        'work_id': fields.many2one('repair.work', 'Work'),    
        'puestostrabajo_id': fields.many2one('repair.puestos_trabajo', 'Puesto'),                         
    }

wizard_puestos_trabajo_work_done()

