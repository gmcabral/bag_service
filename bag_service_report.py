# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2010 Thymbra
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields,osv
import tools

class repair_report(osv.osv):
    _name = "repair.report"
    _description = "Repair Orders"
    _auto = False
    _columns = {
        'date': fields.date('Fecha', readonly=True),
        'name': fields.char('Numero Orden',size=24,required=False, readonly=True),
        'type': fields.char('Tipo',size=128, readonly=True),        
        'year': fields.char('Ano',size=128, readonly=True),        
        'day': fields.char('Dia', size=128, readonly=True),
        'state_id':fields.many2one('bag.state', 'Estado', readonly=True),
        'partner_id':fields.many2one('res.partner', 'Cliente', readonly=True),
        'airline_id':fields.many2one('bag.airline', 'Aerolinea', readonly=True),        
        'scale_id': fields.many2one('bag.scale', 'Escala'),        
        #'address_id':fields.many2one('res.partner.address', 'Domicilio Cliente', readonly=True),
        'date_promised':fields.date('Fecha Prometida', readonly=True),
        'date_return':fields.date('Fecha Entregado', readonly=True),        
        'create_uid':fields.many2one('res.users', 'Usuario', readonly=True),
        'demora':fields.float('Demora Dias', digits=(16,2), readonly=True),
        'demora_pasada':fields.float('Demora Pasada', digits=(16,2), readonly=True),
        'price': fields.float('Importe', readonly=True),
        'nbr': fields.integer('Lineas', readonly=True),
        'month':fields.selection([('01','01 - Ene'), ('02','02 - Feb'), ('03','03 - Mar'), ('04','04 - Abr'), ('05','05 - May'), ('06','06 - Jun'),
                          ('07','07 - Jul'), ('08','08 - Ago'), ('09','09 - Sep'), ('10','10 - Oct'), ('11','11 - Nov'), ('12','12 - Dic')],'Mes',readonly=True),

    }
    _order = 'name desc, date desc'
    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'repair_report')
        cr.execute("""
            create or replace view repair_report as (
                select
                    r.id,
                    r.name,
                    r.type,
                    r.date as date,
                    to_char(r.date, 'YYYY') as year,
                    to_char(r.date, 'MM') as month,
                    to_char(r.date, 'YYYY-MM-DD') as day,
                    r.state_id,
                    r.date_promised,
                    r.date_return,                    
                    --r.address_id,
                    r.partner_id,
                    r.airline_id,
                    r.scale_id,
                    r.create_uid,
                    extract(epoch from age(r.date_return,r.date))/(24*60*60)::decimal(16,2) as demora,
                    extract(epoch from age(r.date_return,r.date_promised))/(24*60*60)::decimal(16,2) as demora_pasada,
                    count(*) as nbr,
                    r.price
                from bag_service r
                group by
                    r.id,
                    r.name,
                    r.type,
                    r.date,
                    r.state_id,
                    r.date_promised,
                    r.date_return,                    
                    --r.address_id,
                    r.partner_id,
                    r.airline_id,
                    r.scale_id,
                    r.create_uid,
                    r.price
                
            )
        """)
repair_report()


class repair_work_report(osv.osv):
    _name = "repair.work.report"
    _description = "Repair Works"
    _auto = False
    _columns = {
        'date': fields.date('Fecha', readonly=True),
        'name': fields.char('Numero Orden',size=24,required=False, readonly=True),
        'type': fields.char('Tipo',size=128, readonly=True),        
        'year': fields.char('Ano',size=128, readonly=True),        
        'day': fields.char('Day', size=128, readonly=True),
        'state_id':fields.many2one('bag.state', 'Estado', readonly=True),
        'partner_id':fields.many2one('res.partner', 'Cliente', readonly=True),
        'airline_id':fields.many2one('bag.airline', 'Aerolinea', readonly=True),        
        'scale_id': fields.many2one('bag.scale', 'Escala'),        
        #'address_id':fields.many2one('res.partner.address', 'Domicilio Cliente', readonly=True),
        'date_promised':fields.date('Fecha Prometida', readonly=True),
        'date_return':fields.date('Fecha Entregado', readonly=True),        
        'create_uid':fields.many2one('res.users', 'Usuario', readonly=True),
        'demora':fields.float('Demora Dias', digits=(16,2), readonly=True),
        'demora_pasada':fields.float('Demora Pasada', digits=(16,2), readonly=True),
        'nbr': fields.integer('Lineas', readonly=True),
        'work_id': fields.many2one('bag.work', 'Trabajo'), 
        'quantity': fields.integer('Cantidad'),               
        'price': fields.float('Precio', digits=(12,2)),                
        'month':fields.selection([('01','01 - Ene'), ('02','02 - Feb'), ('03','03 - Mar'), ('04','04 - Abr'), ('05','05 - May'), ('06','06 - Jun'),
                          ('07','07 - Jul'), ('08','08 - Ago'), ('09','09 - Sep'), ('10','10 - Oct'), ('11','11 - Nov'), ('12','12 - Dic')],'Month',readonly=True),

    }
    _order = 'name desc, date desc'
    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'repair_work_report')
        cr.execute("""
            create or replace view repair_work_report as (
                select
                    b.id,
                    r.name,
                    r.type,
                    r.date as date,
                    to_char(r.date, 'YYYY') as year,
                    to_char(r.date, 'MM') as month,
                    to_char(r.date, 'YYYY-MM-DD') as day,
                    r.state_id,
                    r.date_promised,
                    r.date_return,                    
                    --r.address_id,
                    r.partner_id,
                    r.airline_id,
                    r.scale_id,
                    r.create_uid,
                    extract(epoch from age(r.date_return,r.date))/(24*60*60)::decimal(16,2) as demora,
                    extract(epoch from age(r.date_return,r.date_promised))/(24*60*60)::decimal(16,2) as demora_pasada,
                    count(*) as nbr,
                    sum(b.quantity * b.price) as price,
                    b.quantity,
                    b.work_id
                from bag_service r, bag_work_to_be_done b
                where b.service_id = r.id
                group by
                    b.id,
                    r.name,
                    r.type,
                    r.date,
                    r.state_id,
                    r.date_promised,
                    r.date_return,                    
                    --r.address_id,
                    r.partner_id,
                    r.airline_id,
                    r.scale_id,
                    r.create_uid,
                    b.quantity,
                    b.work_id
                
            )
        """)
repair_work_report()
