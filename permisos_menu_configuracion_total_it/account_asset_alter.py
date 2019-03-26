# -*- coding: utf-8 -*-

from openerp import models, fields, api
import base64
from openerp.osv import osv


class res_users(models.Model):
	_inherit='res.users'

	
	@api.one
	def write(self,vals):
		if vals:
			for key, value in vals.items():
				if str(type(key)) == "<type 'str'>" or str(type(key)) == "<type 'unicode'>":
					sp = key.split('_')
					if len(sp) == 3:
						if sp[0] == 'in' and sp[1] == 'group':
							group = self.env['res.groups'].search([('id','=',int(sp[2]))])[0]
							if group.name == 'Menu Configuracion Total':
								if self.env.uid == 1:
									return super(res_users,self).write(vals)
								else:
									raise osv.except_osv('Alerta!', u'No se encuentra autorizado al Grupo Configuración Total')

		return super(res_users,self).write(vals)