# -*- coding: utf-8 -*-
from openerp.http import Controller
from openerp.http import request, route
import decimal
import openerp.http as http
from openerp import models, fields, api
import base64
from openerp.osv import osv
import decimal
import sys, traceback


class models_asiento_dividir(http.Controller):

    @http.route('/asientos_ojala11', type='http', website=True)
    def tabla_static_index315252(self, **kw):
        try:

            request.cr.execute("""select aml.id,debit,credit from account_move am inner join account_move_line aml on aml.move_id = am.id where am.id = 28855 """)
            rpt = http.request._cr.fetchall()
            lineas_asiento = []
            lineas_asiento_ids = []

            for elem in rpt:
                  lineas_asiento.append([elem[0],elem[1],elem[2]])
                  lineas_asiento_ids.append(elem[0])

            asientos = [29566,29567,29568,29569,29570,29572,29573,29574,29575,29577,29578,29579,29580,29581,29582,29583,29584,29585,29586,29587,29588,29589,29591,29592,29593,29594,29595,29596,29597,29598,29599,29600,29601,29603,29604,29605,29606,29607,29608,29609,29611]      
            
            ini = 0
            maximo = 25
            fin = 25

            for i in asientos:
                  monto_total = 0
                  for j in lineas_asiento[ini:maximo]:
                        monto_total += j[1] - j[2]

                  request.cr.execute(""" UPDATE account_move_line set move_id = """ +str(i)+ """  where id in """ + str(tuple(lineas_asiento_ids[ini:maximo])))
                  ini += 25
                  maximo += 25

                  vals= {
                        'account_id': request.env['account.account'].search([('code','=','5931')])[0].id,
                        'name':'INVENTARIO INICIAL 1',
                        'journal_id':request.env['account.move'].search([('id','=',i)])[0].journal_id.id,
                        'period_id':request.env['account.move'].search([('id','=',i)])[0].period_id.id,
                        'debit':0,
                        'credit':0,
                        'move_id':i,
                  }
                  if monto_total != 0:
                        if monto_total >0:
                              vals['credit'] = monto_total
                              request.env['account.move.line'].create(vals)
                        else:
                              vals['debit'] = -monto_total
                              request.env['account.move.line'].create(vals)

            return 'Finish'
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            t= traceback.format_exception(exc_type, exc_value,exc_traceback)
            return str(t) 

