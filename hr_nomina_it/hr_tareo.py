# -*- encoding: utf-8 -*-
from openerp     import models, fields, api
from openerp.osv import osv, expression
from datetime    import datetime, timedelta
from calendar    import monthrange
import pprint
import codecs
import base64
import decimal
from reportlab.lib.enums import TA_JUSTIFY,TA_CENTER,TA_RIGHT

from reportlab.pdfgen          import canvas
from reportlab.lib.units       import inch
from reportlab.lib.colors      import magenta, red , black , blue, gray, Color, HexColor
from reportlab.pdfbase         import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes   import letter, A4, landscape
from reportlab.platypus        import SimpleDocTemplate, Table, TableStyle,BaseDocTemplate, PageTemplate, Frame
from reportlab.lib             import colors
from reportlab.lib.styles      import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus        import Paragraph, Table, PageBreak, Spacer, FrameBreak,Image
from reportlab.lib.units       import  cm,mm
from reportlab.lib.utils       import simpleSplit
from cgi                       import escape
from reportlab                 import platypus
	
class hr_concepto_line(models.Model):
	_name = 'hr.concepto.line'

	tareo_line_id = fields.Many2one('hr.tareo.line','Padre')

	concepto_id   = fields.Many2one('hr.lista.conceptos','Concepto', required=True)
	payroll_group = fields.Selection([('1','Ingreso'),
									  ('2','Descuentos de la Base'),
									  ('3','Aportes Trabajador'),
									  ('4','Aportes Empleador'),
									  ('5','Descuentos del Neto'),
									  ('6','Neto'),], 'Grupo Planilla', related="concepto_id.payroll_group")
	monto         = fields.Float('Monto')


class hr_tareo_line(models.Model):
	_name = 'hr.tareo.line'

	state               = fields.Selection([('close','Cerrado'),('open','Abierto')],related='tareo_id.state')
	codigo_trabajador   = fields.Char(u'Código')
	basica              = fields.Float('Básico', digits=(12,2))
	a_familiar          = fields.Float('A. Familiar', readonly=1, digits=(12,2))
	vacaciones          = fields.Float('Vacaciones', digits=(12,2))
	subsidiomaternidad  = fields.Float('Subsidio Maternidad', digits=(12,2))
	subsidioincapacidad = fields.Float('Subsidio Incapacidad', digits=(12,2))
	neto       			= fields.Float('Neto', digits=(12,2))
	tareo_id            = fields.Many2one('hr.tareo', 'Detalle')

	#PESTAÑA EMPLEADO
	employee_id       = fields.Many2one('hr.employee', "Empleado")
	dni               = fields.Char('DNI', size=20) #aparece en vista form
	apellido_paterno  = fields.Char('Apellido Paterno', size=20, readonly=1) #aparece en vista form
	apellido_materno  = fields.Char('Apellido Materno', size=20, readonly=1) #aparece en vista form
	nombre            = fields.Char('Nombres', size=30, readonly=1) #aparece en vista form
	cargo             = fields.Many2one('hr.job','Cargo', size=50, readonly=1)
	afiliacion        = fields.Many2one('hr.table.membership','Afiliación')
	zona              = fields.Char('Zona')
	tipo_comision     = fields.Boolean('Tipo Comisión')

	#PESTAÑA INGRESOS
	basica_first                   = fields.Float('Básico', digits=(12,2))
	a_familiar_first               = fields.Float('A. Familiar', readonly=1, digits=(12,2))
	dias_trabajador                = fields.Integer('Dias Trabajados')
	horas_ordinarias_trabajadas    = fields.Float('Horas Ordinarias Trabajadas', digits=(12,2))
	dias_vacaciones                = fields.Float(u'Días Vacaciones', digits=(12,2))
	num_days_subs                  = fields.Integer(u'Días subsidiados')
	horas_extra_diurna             = fields.Float('Horas Extras Diurnas', digits=(12,2))
	horas_extra_nocturna           = fields.Float('Horas Extras Nocturna', digits=(12,2))
	horas_extra_descanso           = fields.Float('Horas Extras 100%', digits=(12,2))
	horas_extra_feriado_diur       = fields.Float('HE feriados diurnas', digits=(12,2))
	horas_extra_feriado_noct       = fields.Float('HE feriados nocturnas', digits=(12,2))
	horas_extra_feriado            = fields.Float('Horas Extras Feriado', digits=(12,2))
	horas_extra_descanso_diurnas   = fields.Float('HE Descanso diurnas', digits=(12,2))
	horas_extra_descanso_nocturnas = fields.Float('HE Descanso nocturnas', digits=(12,2))
	descansos_medicos_permisos     = fields.Integer(u'Descansos médicos o permisos')
	total_ingresos 				   = fields.Float('Total', compute="compute_total_ingresos")
	
	conceptos_ingresos_lines       = fields.One2many('hr.concepto.line', 'tareo_line_id','lineas', domain=[('payroll_group','=','1')])

	#PESTAÑA DESCUENTOS DE LA BASE
	dias_suspension_perfecta        = fields.Integer('Dias Suspensión Perfecta')
	dias_suspension_imperfecta      = fields.Integer('Dias Suspensión Imperfecta')
	tardanza_horas                  = fields.Float('Tardanza Horas', digits=(12,2))
	total_descuentos_base 			= fields.Float('Total', compute="compute_total_descuentos_base")
	
	conceptos_descuentos_base_lines = fields.One2many('hr.concepto.line', 'tareo_line_id','lineas', domain=[('payroll_group','=','2')])
	
	#PESTAÑA APORTES TRABAJADOR
	total_aportes_trabajador 		   = fields.Float('Total', compute="compute_total_aportes_trabajador")

	conceptos_aportes_trabajador_lines = fields.One2many('hr.concepto.line', 'tareo_line_id','lineas', domain=[('payroll_group','=','3')])

	#PESTAÑA APORTES EMPLEADOR
	total_aportes_empleador 		  = fields.Float('Total', compute="compute_total_aportes_empleador")

	conceptos_aportes_empleador_lines = fields.One2many('hr.concepto.line', 'tareo_line_id','lineas', domain=[('payroll_group','=','4')])

	#PESTAÑA DESCUENTOS NETO
	total_descuento_neto 		    = fields.Float('Total', compute="compute_total_descuento_neto")

	conceptos_descuentos_neto_lines = fields.One2many('hr.concepto.line', 'tareo_line_id','lineas', domain=[('payroll_group','=','5')])

	#PESTAÑA NETO
	importe_vac			 = fields.Char(u'Importe de Vacaciones N° OP')

	conceptos_neto_lines = fields.One2many('hr.concepto.line', 'tareo_line_id','lineas', domain=[('payroll_group','=','6')])










	total_remunerable              = fields.Float('Total Remun. Computable', digits=(12,2))
	tipo_suspension_perfecta       = fields.Char('Tipo Suspensión Perfecta')
	tipo_suspension_imperfecta     = fields.Char('Tipo Suspensión Imperfecta')

	# horas extras diurnas y nocturnas para feriados

	descuento_dominical = fields.Float('Descuento Dominical', digits=(12,2))

	total_horas_extras         = fields.Float('Total Horas Extras', digits=(12,2))
	total_horas_extras_horas   = fields.Float('Horas', digits=(12,2))
	total_horas_extras_minutos = fields.Float('Minutos', digits=(12,2))

	####
	vacaciones_trunca    = fields.Float('Vacaciones Trunca', digits=(12,2))
	monto_boni_grati_liq = fields.Float('bonificacion liq', digits=(12,2))	
	h_25                 = fields.Float('H_25%', digits=(12,2))
	h_35                 = fields.Float('H_35%', digits=(12,2))
	h_100                = fields.Float('H_100%', digits=(12,2))

	otros_ingreso   = fields.Float('Otros Ingreso', digits=(12,2))
	tardanzas       = fields.Float('Tardanzas', digits=(12,2))
	inasistencias   = fields.Float('Inasistencias', digits=(12,2))
	dscto_domi      = fields.Float('Dscto. Domi.', digits=(12,2))
	rmb             = fields.Float('RMB', digits=(12,2))
	onp             = fields.Float('ONP', digits=(12,2))
	afp_jub         = fields.Float('AFP_JUB', digits=(12,2))
	afp_psi         = fields.Float('AFP_PSI', digits=(12,2))
	afp_com         = fields.Float('AFP_COM', digits=(12,2))
	quinta_cat      = fields.Float('5TA CAT', digits=(12,2))
	total_descuento = fields.Float('Total Descuento', digits=(12,2))
	neto            = fields.Float('NETO', digits=(12,2))
	neto_sueldo     = fields.Float('NETO SUELDO', digits=(12,2))
	neto_vacaciones = fields.Float('NETO VACACIONES', digits=(12,2))
	adelantos       = fields.Float('Adelantos', digits=(12,2))
	prestamos       = fields.Float('Prestamos', digits=(12,2))
	otros_dct       = fields.Float('Otros Descuentos', digits=(12,2))
	saldo_sueldo    = fields.Float('Saldo a Pagar Sueldo', digits=(12,2))
	essalud         = fields.Float('ESSALUD', digits=(12,2))
	senaty          = fields.Float('SENATI', digits=(12,2))
	rma_pi          = fields.Float('RMA PI', digits=(12,2))
	dsc_afp         = fields.Float('DSC AFP', digits=(12,2))
	cts             = fields.Float('CTS', digits=(12,2))
	gratificacion   = fields.Float('Gratificación', digits=(12,2))
	gratificacion_extraordinaria      = fields.Float('Gratificación Trunca', digits=(12,2))
	gratificacion_extraordinaria_real = fields.Float('Gratificación Extraordinaria', digits=(12,2))
	centro_costo                      = fields.Many2one('hr.distribucion.gastos','Centro C.')
	
	# aditional concepts from email
	sctr         = fields.Float('SCTR', digits=(12,2))
	eps          = fields.Float('EPS %', digits=(12,2))
	bonificacion = fields.Float('Bonificación', digits=(12,2))
	
	comision     = fields.Float('Conmisión', digits=(12,2))
	boni_grati   = fields.Float('Bonificación de Gratificación', digits=(12,2))

	# main id
	
	cta_prestamo  = fields.Many2one('account.account','ctaprestamo')	
	total_boleta  = fields.Float('Total boleta', digits=(12,2))

	# dias subsidiados por materniadad
	num_days_sub_mother = fields.Integer('Días Subsidiados Maternidad')


	@api.one
	def compute_total_ingresos(self):
		res = 0
		for line in self.conceptos_ingresos_lines:
			res += line.monto
		self.total_ingresos = res

	@api.one
	def compute_total_descuentos_base(self):
		res = 0
		for line in self.conceptos_descuentos_base_lines:
			res += line.monto
		self.total_descuentos_base = res

	@api.one
	def compute_total_aportes_trabajador(self):
		res = 0
		for line in self.conceptos_aportes_trabajador_lines:
			res += line.monto
		self.total_aportes_trabajador = res

	@api.one
	def compute_total_aportes_empleador(self):
		res = 0
		for line in self.conceptos_aportes_empleador_lines:
			res += line.monto
		self.total_aportes_empleador = res

	@api.one
	def compute_total_descuento_neto(self):
		res = 0
		for line in self.conceptos_descuentos_neto_lines:
			res += line.monto
		self.total_descuento_neto = res

	@api.onchange('dni',
				  'nombre',
				  'apellido_paterno',
				  'apellido_materno',
				  'cargo',
				  'afiliacion',
				  'tipo_comision',
				  'zona',
				  'basica_first',
				  'a_familiar_first',
				  'dias_trabajador',
				  'horas_ordinarias_trabajadas',
				  'dias_vacaciones',
				  'num_days_subs',
				  'horas_extra_diurna',
				  'horas_extra_nocturna',
				  'horas_extra_descanso',
				  'horas_extra_feriado_diur',
				  'horas_extra_feriado_noct',
				  'horas_extra_feriado',
				  'horas_extra_descanso_diurnas',
				  'horas_extra_descanso_nocturnas',
				  'dias_suspension_perfecta',
				  'dias_suspension_imperfecta',
				  'tardanza_horas',
				  'descansos_medicos_permisos')
	def onchange_all(self):
		htl = self.env['hr.tareo.line'].search([('id','=',self.env.context['active_id'])])[0]
		hhe = self.env['hr.horas.extra'].search([])[0]
		for con_in in self.conceptos_ingresos_lines:
			if con_in.concepto_id.code == '001': #basico
				con_in.monto = (self.basica_first/30.00 * (self.dias_trabajador+self.descansos_medicos_permisos)) if not htl.employee_id.is_practicant else 0
			if con_in.concepto_id.code == '002': #asignacion familiar
				if (self.dias_trabajador+self.descansos_medicos_permisos) == htl.dias_suspension_perfecta:
					con_in.monto = 0
				else:
					con_in.monto = self.a_familiar_first
			if con_in.concepto_id.code == '004': #VACACIONES
				bas = self.basica_first
				if htl.dias_vacaciones >= 30:
					bas += self.a_familiar_first
				con_in.monto = (bas)/30.00*htl.dias_vacaciones
			if con_in.concepto_id.code == '006': #VACACIONES TRUNCAS
				hl = self.env['hr.liquidaciones.lines.vac'].search([('liquidacion_id.period_id','=',htl.tareo_id.periodo.id),('employee_id','=',htl.employee_id.id)])
				res = 0
				for line in hl:
					res += line.total_holidays
				con_in.monto = res
			if con_in.concepto_id.code == '007': #H 25%
				con_in.monto = (((self.basica_first+self.a_familiar_first)/30.00/8.00*hhe.he_diurnas))*self.horas_extra_diurna
			if con_in.concepto_id.code == '008': #H 35%
				con_in.monto = (((self.basica_first+self.a_familiar_first)/30.00/8.00*hhe.he_nocturnas))*self.horas_extra_nocturna
			if con_in.concepto_id.code == '009': #H 100%
				con_in.monto = ((self.basica_first+self.a_familiar_first)/30.00/8.00*hhe.he_cien_p*self.horas_extra_descanso)+((self.basica_first+self.a_familiar_first)/30.00/8.00*hhe.he_diurnas*hhe.he_fer_diur*self.horas_extra_feriado_diur)+((self.basica_first+self.a_familiar_first)/30.00/8.00*hhe.he_nocturnas*hhe.he_fer_noct*self.horas_extra_feriado_noct)+((self.basica_first+self.a_familiar_first)/30.00/8.00*hhe.he_feriados*self.horas_extra_feriado)+((self.basica_first+self.a_familiar_first)/30.00/8.00*hhe.he_diurnas*hhe.he_descansos_diurno*self.horas_extra_descanso_diurnas)+((self.basica_first+self.a_familiar_first)/30.00/8.00*hhe.he_nocturnas*hhe.he_descansos_nocturno*self.horas_extra_descanso_nocturnas)
			if con_in.concepto_id.code == '012': #practicante
				con_in.monto = ((self.basica_first+self.a_familiar_first)/30.00 * (self.dias_trabajador+self.descansos_medicos_permisos)) if htl.employee_id.is_practicant else 0
			if con_in.concepto_id.code == '014': #INDEMNIZACION
				if con_in.monto==0:
					hl = self.env['hr.liquidaciones.lines.vac'].search([('liquidacion_id.period_id','=',htl.tareo_id.periodo.id),('employee_id','=',htl.employee_id.id)])
					res = 0
					for line in hl:
						res += line.compensation
					con_in.monto = res

			if con_in.concepto_id.code == '017': #CTS
				hl = self.env['hr.liquidaciones.lines.cts'].search([('liquidacion_id.period_id','=',htl.tareo_id.periodo.id),('employee_id','=',htl.employee_id.id)])
				res = 0
				for line in hl:
					res += line.total_payment
				hctl = self.env['hr.cts.line'].search([('cts.period_id','=',htl.tareo_id.periodo.id),('employee_id','=',htl.employee_id.id)])
				for line in hctl:
					res += line.cts_soles
				con_in.monto = res
			if con_in.concepto_id.code == '018': #GRATIFICACIONES
				hrl = self.env['hr.reward.line'].search([('reward.period_id','=',htl.tareo_id.periodo.id),('employee_id','=',htl.employee_id.id)])
				res = 0
				for line in hrl:
					res += line.total_reward
				con_in.monto = res
			if con_in.concepto_id.code == '019': #GRATIFICACIONES TRUNCAS
				hl = self.env['hr.liquidaciones.lines.grat'].search([('liquidacion_id.period_id','=',htl.tareo_id.periodo.id),('employee_id','=',htl.employee_id.id)])
				res = 0
				for line in hl:
					res += line.total_months
				con_in.monto = res
			if con_in.concepto_id.code == '020': #BONO DE GRATIFICACION
				hl = self.env['hr.liquidaciones.lines.grat'].search([('liquidacion_id.period_id','=',htl.tareo_id.periodo.id),('employee_id','=',htl.employee_id.id)])
				res = 0
				for line in hl:
					res += line.bonus
				hrl = self.env['hr.reward.line'].search([('reward.period_id','=',htl.tareo_id.periodo.id),('employee_id','=',htl.employee_id.id)])
				for line in hrl:
					res += line.plus_9
				con_in.monto = res


			# if con_in.concepto_id.code == '005': #COMPRENSA VAC
				# if con_in.monto==0:
					# con_in.monto = i.monto

		for con_desc_b in self.conceptos_descuentos_base_lines:
			if con_desc_b.concepto_id.code == '024': #tardanzas
				con_desc_b.monto = (((self.basica_first+self.a_familiar_first)/30.00)/8.00)*self.tardanza_horas
			if con_desc_b.concepto_id.code == '025': #inasistencias
				con_desc_b.monto = (self.basica_first/30.00)*self.dias_suspension_perfecta

		for con_ap_trab in self.conceptos_aportes_trabajador_lines:
			if con_ap_trab.concepto_id.code == '028': #ONP
				if self.afiliacion.code:
					raw_base = 0
					if self.afiliacion.code == 'ONP':
						for item in self.conceptos_ingresos_lines: #SUMA DE INGRESOS
							hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
							if len(hcrl) > 0:
								hcrl = hcrl[0]
								if hcrl.onp and hcrl.rmb and not hcrl.neto_vac:
									raw_base += item.monto
						for item in self.conceptos_descuentos_base_lines: #RESTA DE DESCUENTOS
							hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
							if len(hcrl) > 0:
								hcrl = hcrl[0]
								if hcrl.onp and hcrl.rmb and not hcrl.neto_vac:
									raw_base -= item.monto
					
						hml = self.env['hr.membership.line'].search([('membership','=',self.afiliacion.id),('periodo','=',self.tareo_id.periodo.id)])
						if len(hml) > 0: #PORCENTAJE DE ONP
							raw_base *= hml[0].tasa_pensiones/100.00

						con_ap_trab.monto = raw_base
					else:
						con_ap_trab.monto = 0
				else:
					con_ap_trab.monto = 0

			if con_ap_trab.concepto_id.code == '065': #ONP VACACIONES CALQUIPA
				if self.afiliacion.code:
					raw_base = 0
					if self.afiliacion.code == 'ONP':
						for item in self.conceptos_ingresos_lines: #SUMA DE INGRESOS
							hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
							if len(hcrl) > 0:
								hcrl = hcrl[0]
								if hcrl.onp and hcrl.neto_vac:
									raw_base += item.monto
						for item in self.conceptos_descuentos_base_lines: #RESTA DE DESCUENTOS
							hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
							if len(hcrl) > 0:
								hcrl = hcrl[0]
								if hcrl.onp and hcrl.neto_vac:
									raw_base -= item.monto
					
						hml = self.env['hr.membership.line'].search([('membership','=',self.afiliacion.id),('periodo','=',self.tareo_id.periodo.id)])
						if len(hml) > 0: #PORCENTAJE DE ONP
							raw_base *= hml[0].tasa_pensiones/100.00

						con_ap_trab.monto = raw_base
					else:
						con_ap_trab.monto = 0
				else:
					con_ap_trab.monto = 0

			if con_ap_trab.concepto_id.code in ['029','030','031']: #AFP (JUB, PSI, COM)
				if self.afiliacion.code:
					raw_base_j = 0
					raw_base_p = 0
					raw_base_c = 0
					if self.afiliacion.code != 'ONP':
						for item in self.conceptos_ingresos_lines: #SUMA DE INGRESOS
							hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
							if len(hcrl) > 0:
								hcrl = hcrl[0]
								if hcrl.afp_fon_pen and hcrl.rmb and not hcrl.neto_vac:
									raw_base_j += item.monto
								if hcrl.afp_pri_se and hcrl.rmb and not hcrl.neto_vac:
									raw_base_p += item.monto
								if htl.employee_id.c_mixta:
									if hcrl.afp_co_mix and hcrl.rmb and not hcrl.neto_vac:
										raw_base_c += item.monto
								else:
									if hcrl.afp_co_va and hcrl.rmb and not hcrl.neto_vac:
										raw_base_c += item.monto
						for item in self.conceptos_descuentos_base_lines: #RESTA DE DESCUENTOS
							hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
							if len(hcrl) > 0:
								hcrl = hcrl[0]
								if hcrl.afp_fon_pen and hcrl.rmb and not hcrl.neto_vac:
									raw_base_j -= item.monto
								if hcrl.afp_pri_se and hcrl.rmb and not hcrl.neto_vac:
									raw_base_p -= item.monto
								if htl.employee_id.c_mixta:
									if hcrl.afp_co_mix and hcrl.rmb and not hcrl.neto_vac:
										raw_base_c -= item.monto
								else:
									if hcrl.afp_co_va:
										raw_base_c -= item.monto
					
						hml = self.env['hr.membership.line'].search([('membership','=',self.afiliacion.id),('periodo','=',self.tareo_id.periodo.id)])
						if len(hml) > 0: #PORCENTAJE DE AFP (JUB, PSI, COM)
							if con_ap_trab.concepto_id.code == '029':
								raw_base_j *= hml[0].tasa_pensiones/100.00
							if con_ap_trab.concepto_id.code == '030':
								if raw_base_p > hml.rma:
									raw_base_p = hml.rma * hml[0].prima/100.00
								else:
									raw_base_p *= hml[0].prima/100.00
							if con_ap_trab.concepto_id.code == '031':
								if htl.employee_id.c_mixta:
									raw_base_c *= hml[0].c_mixta/100.00
								else:
									raw_base_c *= hml[0].c_variable/100.00

						if con_ap_trab.concepto_id.code == '029':
							con_ap_trab.monto = raw_base_j
						if con_ap_trab.concepto_id.code == '030':
							con_ap_trab.monto = raw_base_p
						if con_ap_trab.concepto_id.code == '031':
							con_ap_trab.monto = raw_base_c
					else:
						if con_ap_trab.concepto_id.code == '029':
							con_ap_trab.monto = 0
						if con_ap_trab.concepto_id.code == '030':
							con_ap_trab.monto = 0
						if con_ap_trab.concepto_id.code == '031':
							con_ap_trab.monto = 0
				else:
					if con_ap_trab.concepto_id.code == '029':
						con_ap_trab.monto = 0
					if con_ap_trab.concepto_id.code == '030':
						con_ap_trab.monto = 0
					if con_ap_trab.concepto_id.code == '031':
						con_ap_trab.monto = 0

			if con_ap_trab.concepto_id.code in ['066','067','068']: #AFP (JUB, PSI, COM) VACACIONES
				if self.afiliacion.code:
					raw_base_j = 0
					raw_base_p = 0
					raw_base_c = 0
					if self.afiliacion.code != 'ONP':
						for item in self.conceptos_ingresos_lines: #SUMA DE INGRESOS
							hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
							if len(hcrl) > 0:
								hcrl = hcrl[0]
								if hcrl.afp_fon_pen and hcrl.neto_vac:
									raw_base_j += item.monto
								if hcrl.afp_pri_se and hcrl.neto_vac:
									raw_base_p += item.monto
								if htl.employee_id.c_mixta:
									if hcrl.afp_co_mix and hcrl.neto_vac:
										raw_base_c += item.monto
								else:
									if hcrl.afp_co_va and hcrl.neto_vac:
										raw_base_c += item.monto
						for item in self.conceptos_descuentos_base_lines: #RESTA DE DESCUENTOS
							hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
							if len(hcrl) > 0:
								hcrl = hcrl[0]
								if hcrl.afp_fon_pen and hcrl.neto_vac:
									raw_base_j -= item.monto
								if hcrl.afp_pri_se and hcrl.neto_vac:
									raw_base_p -= item.monto
								if htl.employee_id.c_mixta:
									if hcrl.afp_co_mix and hcrl.neto_vac:
										raw_base_c -= item.monto
								else:
									if hcrl.afp_co_va:
										raw_base_c -= item.monto
					
						hml = self.env['hr.membership.line'].search([('membership','=',self.afiliacion.id),('periodo','=',self.tareo_id.periodo.id)])
						if len(hml) > 0: #PORCENTAJE DE AFP (JUB, PSI, COM)
							if con_ap_trab.concepto_id.code == '066':
								raw_base_j *= hml[0].tasa_pensiones/100.00
							if con_ap_trab.concepto_id.code == '067':
								if raw_base_p > hml.rma:
									raw_base_p = hml.rma * hml[0].prima/100.00
								else:
									raw_base_p *= hml[0].prima/100.00
							if con_ap_trab.concepto_id.code == '068':
								if htl.employee_id.c_mixta:
									raw_base_c *= hml[0].c_mixta/100.00
								else:
									raw_base_c *= hml[0].c_variable/100.00

						if con_ap_trab.concepto_id.code == '066':
							con_ap_trab.monto = raw_base_j
						if con_ap_trab.concepto_id.code == '067':
							con_ap_trab.monto = raw_base_p
						if con_ap_trab.concepto_id.code == '068':
							con_ap_trab.monto = raw_base_c
					else:
						if con_ap_trab.concepto_id.code == '066':
							con_ap_trab.monto = 0
						if con_ap_trab.concepto_id.code == '067':
							con_ap_trab.monto = 0
						if con_ap_trab.concepto_id.code == '068':
							con_ap_trab.monto = 0
				else:
					if con_ap_trab.concepto_id.code == '066':
						con_ap_trab.monto = 0
					if con_ap_trab.concepto_id.code == '067':
						con_ap_trab.monto = 0
					if con_ap_trab.concepto_id.code == '068':
						con_ap_trab.monto = 0

			if con_ap_trab.concepto_id.code == '033': #5TA CATEGORIA NORMAL
				hfcl = self.env['hr.five.category.lines'].search([('five_category_id.fiscalyear','=',htl.tareo_id.periodo.fiscalyear_id.id),('employee_id','=',htl.employee_id.id)])
				res = 0
				for line in hfcl:
					if htl.tareo_id.periodo.code.split('/')[0] == '01':
						res += line.janu_amount
					if htl.tareo_id.periodo.code.split('/')[0] == '02':
						res += line.febr_amount
					if htl.tareo_id.periodo.code.split('/')[0] == '03':
						res += line.marc_amount
					if htl.tareo_id.periodo.code.split('/')[0] == '04':
						res += line.apri_amount
					if htl.tareo_id.periodo.code.split('/')[0] == '05':
						res += line.mayo_amount
					if htl.tareo_id.periodo.code.split('/')[0] == '06':
						res += line.june_amount
					if htl.tareo_id.periodo.code.split('/')[0] == '07':
						res += line.july_amount
					if htl.tareo_id.periodo.code.split('/')[0] == '08':
						res += line.agos_amount
					if htl.tareo_id.periodo.code.split('/')[0] == '09':
						res += line.sept_amount
					if htl.tareo_id.periodo.code.split('/')[0] == '10':
						res += line.octo_amount
					if htl.tareo_id.periodo.code.split('/')[0] == '11':
						res += line.nove_amount
					if htl.tareo_id.periodo.code.split('/')[0] == '12':
						res += line.dece_amount

				raw_base_100 = 0
				raw_base_rest = 0
				for item in self.conceptos_ingresos_lines: #SUMA DE INGRESOS
					hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
					if len(hcrl) > 0:
						hcrl = hcrl[0]
						if hcrl.rmb:
							raw_base_100 += item.monto
						if hcrl.rmb and hcrl.neto_vac:
							raw_base_rest += item.monto

				neto_vac_percent = (raw_base_rest * 100.00 / float(raw_base_100)) if float(raw_base_100) else 0
				sueldos_percent  = 100.00 - neto_vac_percent
				con_ap_trab.monto = res * sueldos_percent/100.00

			if con_ap_trab.concepto_id.code == '069': #5TA CATEGORIA VACACIONES
				hfcl = self.env['hr.five.category.lines'].search([('five_category_id.fiscalyear','=',htl.tareo_id.periodo.fiscalyear_id.id),('employee_id','=',htl.employee_id.id)])
				res = 0
				for line in hfcl:
					if htl.tareo_id.periodo.code.split('/')[0] == '01':
						res += line.janu_amount
					if htl.tareo_id.periodo.code.split('/')[0] == '02':
						res += line.febr_amount
					if htl.tareo_id.periodo.code.split('/')[0] == '03':
						res += line.marc_amount
					if htl.tareo_id.periodo.code.split('/')[0] == '04':
						res += line.apri_amount
					if htl.tareo_id.periodo.code.split('/')[0] == '05':
						res += line.mayo_amount
					if htl.tareo_id.periodo.code.split('/')[0] == '06':
						res += line.june_amount
					if htl.tareo_id.periodo.code.split('/')[0] == '07':
						res += line.july_amount
					if htl.tareo_id.periodo.code.split('/')[0] == '08':
						res += line.agos_amount
					if htl.tareo_id.periodo.code.split('/')[0] == '09':
						res += line.sept_amount
					if htl.tareo_id.periodo.code.split('/')[0] == '10':
						res += line.octo_amount
					if htl.tareo_id.periodo.code.split('/')[0] == '11':
						res += line.nove_amount
					if htl.tareo_id.periodo.code.split('/')[0] == '12':
						res += line.dece_amount

				raw_base_100 = 0
				raw_base_rest = 0
				for item in self.conceptos_ingresos_lines: #SUMA DE INGRESOS
					hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
					if len(hcrl) > 0:
						hcrl = hcrl[0]
						if hcrl.rmb:
							raw_base_100 += item.monto
						if hcrl.rmb and hcrl.neto_vac:
							raw_base_rest += item.monto

				neto_vac_percent = (raw_base_rest * 100.00 / float(raw_base_100)) if raw_base_100 != 0 else 0
				sueldos_percent  = 100.00 - neto_vac_percent
				con_ap_trab.monto = res * neto_vac_percent/100.00

			if con_ap_trab.concepto_id.code == '034': #EsSalud Vida
				if htl.employee_id.essalud_vida:
					con_ap_trab.monto = self.env['hr.parameters'].search([('num_tipo','=',2)])[0].monto/100.00

			if con_ap_trab.concepto_id.code == '036': #Fondo Jubilación
				if htl.employee_id.fondo_jub:
					raw_base = 0
					for item in self.conceptos_ingresos_lines: #SUMA DE INGRESOS
						hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
						if len(hcrl) > 0:
							hcrl = hcrl[0]
							if hcrl.jubilacion:
								raw_base += item.monto
					for item in self.conceptos_descuentos_base_lines: #RESTA DE DESCUENTOS
						hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
						if len(hcrl) > 0:
							hcrl = hcrl[0]
							if hcrl.jubilacion:
								raw_base -= item.monto
					raw_base *= self.env['hr.parameters'].search([('num_tipo','=',3)])[0].monto/100.00
					con_ap_trab.monto = raw_base

		for con_ap_empl in self.conceptos_aportes_empleador_lines:
			if con_ap_empl.concepto_id.code == '038': #EsSalud
				if not htl.employee_id.is_practicant:
					raw_base = 0
					# if htl.dias_trabajador == htl.dias_suspension_perfecta:
					# 	con_ap_empl.monto = 0
					# else:
					for item in self.conceptos_ingresos_lines: #SUMA DE INGRESOS
						hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
						if len(hcrl) > 0:
							hcrl = hcrl[0]
							if hcrl.essalud:
								raw_base += item.monto
					for item in self.conceptos_descuentos_base_lines: #RESTA DE DESCUENTOS
						hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
						if len(hcrl) > 0:
							hcrl = hcrl[0]
							if hcrl.essalud:
								raw_base -= item.monto

					raw_base *= self.env['hr.parameters'].search([('num_tipo','=',4)])[0].monto/100.00
					cond = self.env['hr.parameters'].search([('num_tipo','=',10000)])[0].monto * self.env['hr.parameters'].search([('num_tipo','=',4)])[0].monto/100.00
					con_ap_empl.monto = max(cond, raw_base)
				else:
					con_ap_empl.monto = 0

			if con_ap_empl.concepto_id.code == '039': #SCTR
				if self.env['res.company'].search([])[0].sctr:
					raw_base = 0
					for item in self.conceptos_ingresos_lines: #SUMA DE INGRESOS
						hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
						if len(hcrl) > 0:
							hcrl = hcrl[0]
							if hcrl.scrt:
								raw_base += item.monto
					for item in self.conceptos_descuentos_base_lines: #RESTA DE DESCUENTOS
						hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
						if len(hcrl) > 0:
							hcrl = hcrl[0]
							if hcrl.scrt:
								raw_base -= item.monto
					raw_base *= self.env['hr.parameters'].search([('num_tipo','=',6)])[0].monto/100.00
					con_ap_empl.monto = raw_base

			if con_ap_empl.concepto_id.code == '040': #EPS / SCTR SALUD
				if htl.employee_id.use_eps:
					raw_base = 0
					for item in self.conceptos_ingresos_lines: #SUMA DE INGRESOS
						hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
						if len(hcrl) > 0:
							hcrl = hcrl[0]
							if hcrl.eps_sctr_salud:
								raw_base += item.monto
					for item in self.conceptos_descuentos_base_lines: #RESTA DE DESCUENTOS
						hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
						if len(hcrl) > 0:
							hcrl = hcrl[0]
							if hcrl.eps_sctr_salud:
								raw_base -= item.monto
					raw_base *= self.env['hr.parameters'].search([('num_tipo','=',5)])[0].monto/100.00
					con_ap_empl.monto = raw_base
					essalud = self.env['hr.concepto.line'].search([('tareo_line_id','=',self.env.context['active_id']),('concepto_id.code','=','038')])
					essalud[0].monto -= raw_base

			if con_ap_empl.concepto_id.code == '041': #SENATI
				if not htl.employee_id.is_practicant:
					if self.env['res.company'].search([])[0].senati:
						raw_base = 0
						for item in self.conceptos_ingresos_lines: #SUMA DE INGRESOS
							hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
							if len(hcrl) > 0:
								hcrl = hcrl[0]
								if hcrl.senati:
									raw_base += item.monto
						for item in self.conceptos_descuentos_base_lines: #RESTA DE DESCUENTOS
							hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
							if len(hcrl) > 0:
								hcrl = hcrl[0]
								if hcrl.senati:
									raw_base -= item.monto
						raw_base *= self.env['hr.parameters'].search([('num_tipo','=',7)])[0].monto/100.00
						con_ap_empl.monto = raw_base
				else:
					con_ap_empl.monto = 0

			if con_ap_empl.concepto_id.code == '044': #AFP 2%
				if self.env['res.company'].search([])[0].afp_2p:
					if self.afiliacion.mem_type == 'private':
						raw_base = 0
						for item in self.conceptos_ingresos_lines: #SUMA DE INGRESOS
							hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
							if len(hcrl) > 0:
								hcrl = hcrl[0]
								if hcrl.afp_2p:
									raw_base += item.monto
						for item in self.conceptos_descuentos_base_lines: #RESTA DE DESCUENTOS
							hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
							if len(hcrl) > 0:
								hcrl = hcrl[0]
								if hcrl.afp_2p:
									raw_base -= item.monto
						raw_base *= self.env['hr.parameters'].search([('num_tipo','=',8)])[0].monto/100.00
						con_ap_empl.monto = raw_base

		for con_desc_n in self.conceptos_descuentos_neto_lines:
			if con_desc_n.concepto_id.code == '045': #ADELANTOS
				ha = self.env['hr.adelanto'].search([('fecha','>=',htl.tareo_id.periodo.date_start),('fecha','<=',htl.tareo_id.periodo.date_stop),('employee','=',htl.employee_id.id)])
				res = 0
				for item in ha:
					res += item.monto
				con_desc_n.monto = res

			if con_desc_n.concepto_id.code == '046': #PRESTAMOS
				ha = self.env['hr.prestamo.lines'].search([('fecha_pago','>=',htl.tareo_id.periodo.date_start),('fecha_pago','<=',htl.tareo_id.periodo.date_stop),('prestamo_id.employee_id','=',htl.employee_id.id),('validacion','=','2')])
				res = 0
				for item in ha:
					res += item.monto
				con_desc_n.monto = res

		for con_neto in self.conceptos_neto_lines:
			if con_neto.concepto_id.code == '047': #RMB
				raw_base = 0
				for item in self.conceptos_ingresos_lines: #SUMA DE INGRESOS
					hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
					if len(hcrl) > 0:
						hcrl = hcrl[0]
						if hcrl.rmb:
							raw_base += item.monto
				for item in self.conceptos_descuentos_base_lines: #RESTA DE DESCUENTOS
					hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
					if len(hcrl) > 0:
						hcrl = hcrl[0]
						if hcrl.rmb:
							raw_base -= item.monto
				con_neto.monto = raw_base

			if con_neto.concepto_id.code == '048': #Total descuentos
				con_neto.monto = self.total_aportes_trabajador + self.total_descuento_neto

			if con_neto.concepto_id.code == '049': #NETO
				rmb = self.env['hr.concepto.line'].search([('tareo_line_id','=',self.env.context['active_id']),('concepto_id.code','=','047')])
				tot_desc = self.env['hr.concepto.line'].search([('tareo_line_id','=',self.env.context['active_id']),('concepto_id.code','=','048')])
				res = 0
				if len(rmb) > 0:
					rmb = rmb[0]
					res += rmb.monto
				if len(tot_desc) > 0:
					tot_desc = tot_desc[0]
					res -= tot_desc.monto
				con_neto.monto = res

			if con_neto.concepto_id.code == '050': #NETO SUELDOS
				raw_base = 0
				for item in self.conceptos_ingresos_lines: #SUMA DE INGRESOS
					hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
					if len(hcrl) > 0:
						hcrl = hcrl[0]
						if hcrl.rmb and not hcrl.neto_vac:
							raw_base += item.monto
				for item in self.conceptos_descuentos_base_lines: #RESTA DE DESCUENTOS
					hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
					if len(hcrl) > 0:
						hcrl = hcrl[0]
						if hcrl.rmb and not hcrl.neto_vac:
							raw_base -= item.monto
				afp_vac = self.env['hr.concepto.line'].search([('tareo_line_id','=',self.env.context['active_id']),('concepto_id.code','in',['065','066','067','068','069'])])
				sum_afp = 0
				for i in afp_vac:
					sum_afp += i.monto
				raw_base -= (htl.total_aportes_trabajador - sum_afp)
				ha = self.env['hr.adelanto'].search([('employee','=',htl.employee_id.id),('fecha','>=',htl.tareo_id.periodo.date_start),('fecha','<=',htl.tareo_id.periodo.date_stop),('adelanto_id.code','=','002')])
				ade = 0
				for i in ha:
					ade += i.monto
				raw_base -= (htl.total_descuento_neto - ade)
				con_neto.monto = raw_base

			if con_neto.concepto_id.code == '051': #NETO VACACIONES
				raw_base = 0
				for item in self.conceptos_ingresos_lines: #SUMA DE INGRESOS
					hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
					if len(hcrl) > 0:
						hcrl = hcrl[0]
						if hcrl.neto_vac:
							raw_base += item.monto
				for item in self.conceptos_descuentos_base_lines: #RESTA DE DESCUENTOS
					hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item.concepto_id.id)])
					if len(hcrl) > 0:
						hcrl = hcrl[0]
						if hcrl.neto_vac:
							raw_base -= item.monto
				afp_vac = self.env['hr.concepto.line'].search([('tareo_line_id','=',self.env.context['active_id']),('concepto_id.code','in',['065','066','067','068','069'])])
				for i in afp_vac:
					raw_base -= i.monto
				ha = self.env['hr.adelanto'].search([('employee','=',htl.employee_id.id),('fecha','>=',htl.tareo_id.periodo.date_start),('fecha','<=',htl.tareo_id.periodo.date_stop),('adelanto_id.code','=','002')])
				ade = 0
				for i in ha:
					ade += i.monto
				raw_base -= ade
				con_neto.monto = raw_base

			if con_neto.concepto_id.code == '053': #OTROS INGRESOS
				rmb = self.env['hr.concepto.line'].search([('tareo_line_id','=',self.env.context['active_id']),('concepto_id.code','=','047')])
				con_neto.monto = self.total_ingresos - (rmb[0].monto if len(rmb) > 0 else 0) - self.total_descuentos_base

			if con_neto.concepto_id.code == '054': #APORTES EMPLEADO
				con_neto.monto = self.total_aportes_empleador
			

	@api.multi
	def open_wizard(self):
		return {
			'type': 'ir.actions.act_window',
			'name': "Detalle Tareo",
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'hr.tareo.line',
			'res_id': self.id,
			'target': 'new',
			'context': {'default_dias_trabajador': 30},
		}

	@api.model
	def create(self, vals):
		t = super(hr_tareo_line, self).create(vals)

		hlc = self.env['hr.lista.conceptos'].search([])
		for concepto in hlc:
			hcl = self.env['hr.concepto.line'].create({
				'concepto_id'  : concepto.id,
				'monto'        : 0,
				'tareo_line_id': t.id,
			})

		return t

	@api.one
	def write(self,vals):
		t = super(hr_tareo_line,self).write(vals)
		self.refresh()
		# self.with_context({'active_id':self.id}).onchange_all()

		if 'avoid_recursion' in vals:
			pass
		else:
			basica   = self.env['hr.concepto.line'].search([('tareo_line_id','=',self.id),('concepto_id.code','=','001')])
			asig_fam = self.env['hr.concepto.line'].search([('tareo_line_id','=',self.id),('concepto_id.code','=','002')])
			vacacion = self.env['hr.concepto.line'].search([('tareo_line_id','=',self.id),('concepto_id.code','=','004')])
			subs_mat = self.env['hr.concepto.line'].search([('tareo_line_id','=',self.id),('concepto_id.code','=','022')])
			subs_inc = self.env['hr.concepto.line'].search([('tareo_line_id','=',self.id),('concepto_id.code','=','023')])
			neto     = self.env['hr.concepto.line'].search([('tareo_line_id','=',self.id),('concepto_id.code','=','049')])
			self.write({
				'avoid_recursion'    : 1,
				'basica'             : basica[0].monto if len(basica) > 0 else 0,
				'a_familiar'         : asig_fam[0].monto if len(asig_fam) > 0 else 0,
				'vacaciones'         : vacacion[0].monto if len(vacacion) > 0 else 0,
				'subsidiomaternidad' : subs_mat[0].monto if len(subs_mat) > 0 else 0,
				'subsidioincapacidad': subs_inc[0].monto if len(subs_inc) > 0 else 0,
				'neto'               : neto[0].monto if len(neto) > 0 else 0,
			})

		# if 'nohacernada' in vals:
		# 	pass
		# else:

		# 	tmp__1 = (self.basica_first /30) * self.dias_trabajador
		# 	self.write({'nohacernada':1,'basica': tmp__1})
			
		# 	tmp__2 = (self.a_familiar)
		# 	# if self.vacaciones>0:
		# 		# tmp__2=0
				

		# 	self.write({'nohacernada':1,'a_familiar': tmp__2})
		# 	self.refresh()

		# 	tmp__3 =  ((self.total_remunerable/30) /8 )* self.horas_extra_diurna* self.env['hr.parameters'].search([])[0].he_diurnas
		# 	self.write({'nohacernada':1,'h_25': tmp__3})

		# 	tmp__4 =  ((self.total_remunerable/30) /8 )* self.horas_extra_nocturna* self.env['hr.parameters'].search([])[0].he_nocturnas
		# 	self.write({'nohacernada':1,'h_35': tmp__4})

		# 	tmp__5 =  ((self.total_remunerable/30) /8 )* self.horas_extra_feriado* self.env['hr.parameters'].search([])[0].he_feriados
		# 	tmp__11 =  ((self.total_remunerable/30) /8 )* self.horas_extra_descanso* self.env['hr.parameters'].search([])[0].he_descansos
		# 	tmp__111 =  ((self.total_remunerable/30) /8 )* self.env['hr.parameters'].search([])[0].he_diurnas* self.env['hr.parameters'].search([])[0].he_descansos_diurno * self.horas_extra_descanso_diurnas
		# 	tmp__112 =  ((self.total_remunerable/30) /8 )* self.env['hr.parameters'].search([])[0].he_nocturnas* self.env['hr.parameters'].search([])[0].he_descansos_nocturno * self.horas_extra_descanso_nocturnas
		# 	self.write({'nohacernada':1,'h_100': tmp__5})
		# 	apara=str(self.env['hr.parameters'].search([])[0].he_fer_noct).split('.')
		# 	montodia= (self.total_remunerable/30) /8 
		# 	montodiaso=montodia*int(apara[0])
		# 	montodiaso=montodiaso+montodiaso*(float(apara[1])/100)
		# 	tmp__5+=   self.horas_extra_feriado_noct* montodiaso

		# 	apara=str(self.env['hr.parameters'].search([])[0].he_fer_diur).split('.')
		# 	montodia= (self.total_remunerable/30) /8 
		# 	montodiaso=montodia*int(apara[0])
		# 	montodiaso=montodiaso+montodiaso*(float(apara[1])/100)
		# 	tmp__5 += self.horas_extra_feriado_diur*montodiaso
		# 	tmp__5 += tmp__11 + tmp__111 + tmp__112

		# 	self.write({'nohacernada':1,'h_100': tmp__5})

		# 	tmp__6 =  round( ((self.total_remunerable/30) /8 )+0.0001,2)* self.tardanza_horas
		# 	self.write({'nohacernada':1,'tardanzas': tmp__6})
		# 	tmp__7 =0
		# 	if self.dias_suspension_perfecta:
		# 		if self.dias_suspension_perfecta>0:
		# 			tmp__7 =  (((self.basica_first/30) )* self.dias_suspension_perfecta)
		# 			# tmp__7 =  (((self.basica_first/30) )* self.dias_suspension_perfecta)+self.a_familiar_first
			
		# 	self.write({'nohacernada':1,'inasistencias': tmp__7})

		# 	tmp__8 = self.horas_extra_diurna + self.horas_extra_nocturna + self.horas_extra_feriado+self.horas_extra_feriado_diur+self.horas_extra_feriado_noct
		# 	self.write({'nohacernada':1,'total_horas_extras': tmp__8})
		# 	self.refresh()

		# 	tmp__9 = int(self.total_horas_extras)
		# 	self.write({'nohacernada':1,'total_horas_extras_horas': tmp__9})
		# 	self.refresh()

		# 	tmp__10 = (self.total_horas_extras - int(self.total_horas_extras) )*60
		# 	self.write({'nohacernada':1,'total_horas_extras_minutos': tmp__10})
			

		# 	self.refresh()

		# 	tmp_1 = self.basica + self.a_familiar + self.vacaciones + self.vacaciones_trunca + self.subsidiomaternidad+self.bonificacion+self.comision
		# 	tmp_1 += self.subsidioincapacidad + self.h_25 + self.h_35 + self.h_100 + self.otros_ingreso 
		# 	self.write({'nohacernada':1,'total_ingreso': tmp_1})
		# 	tmp_2 = tmp_1 - self.tardanzas - self.inasistencias - self.dscto_domi
		# 	self.write({'nohacernada':1,'rmb': tmp_2})

		# 	####
			
		# 	trib_1= 0
		# 	for iij in self.env['hr.concepto.remunerativo.line'].search([('afecto_tributo','=',True)]):
		# 		if iij.concepto.code == '001':
		# 			trib_1 += self.basica
		# 		if iij.concepto.code == '002':
		# 			trib_1 += self.a_familiar
		# 		if iij.concepto.code == '003':
		# 			trib_1 += self.vacaciones
		# 		if iij.concepto.code == '004':
		# 			trib_1 += self.vacaciones_trunca
		# 		if iij.concepto.code == '005':
		# 			trib_1 += self.gratificacion
		# 		if iij.concepto.code == '006':
		# 			trib_1 += self.subsidiomaternidad
		# 		if iij.concepto.code == '007':
		# 			trib_1 += self.gratificacion_extraordinaria
		# 		if iij.concepto.code == '008':
		# 			trib_1 += self.bonificacion
		# 		if iij.concepto.code == '009':
		# 			trib_1 += self.comision
		# 		if iij.concepto.code == '010':
		# 			trib_1 += self.boni_grati

		# 	trib_2= 0
		# 	for iij in self.env['hr.concepto.remunerativo.line'].search([('afecto_afp','=',True)]):
		# 		if iij.concepto.code == '001':
		# 			trib_2 += self.basica
		# 		if iij.concepto.code == '002':
		# 			trib_2 += self.a_familiar
		# 		if iij.concepto.code == '003':
		# 			trib_2 += self.vacaciones
		# 		if iij.concepto.code == '004':
		# 			trib_2 += self.vacaciones_trunca
		# 		if iij.concepto.code == '005':
		# 			trib_2 += self.gratificacion
		# 		if iij.concepto.code == '006':
		# 			trib_2 += self.subsidiomaternidad
		# 		if iij.concepto.code == '007':
		# 			trib_2 += self.gratificacion_extraordinaria
		# 		if iij.concepto.code == '008':
		# 			trib_2 += self.bonificacion
		# 		if iij.concepto.code == '009':
		# 			trib_2 += self.comision
		# 		if iij.concepto.code == '010':
		# 			trib_2 += self.boni_grati			

		# 	trib_3= 0
		# 	for iij in self.env['hr.concepto.remunerativo.line'].search([('afecto_aportes','=',True)]):
		# 		if iij.concepto.code == '001':
		# 			trib_3 += self.basica
		# 		if iij.concepto.code == '002':
		# 			trib_3 += self.a_familiar
		# 		if iij.concepto.code == '003':
		# 			trib_3 += self.vacaciones
		# 		if iij.concepto.code == '004':
		# 			trib_3 += self.vacaciones_trunca
		# 		if iij.concepto.code == '005':
		# 			trib_3 += self.gratificacion
		# 		if iij.concepto.code == '006':
		# 			trib_3 += self.subsidiomaternidad
		# 		if iij.concepto.code == '007':
		# 			trib_3 += self.gratificacion_extraordinaria
		# 		if iij.concepto.code == '008':
		# 			trib_3 += self.bonificacion
		# 		if iij.concepto.code == '009':
		# 			trib_3 += self.comision
		# 		if iij.concepto.code == '010':
		# 			trib_3 += self.boni_grati					

		# 	if self.afiliacion.id:
		# 		t_opm=self.env['hr.membership.line'].search( [('periodo','=',self.tareo_id.periodo.id),('membership','=',self.afiliacion.id)] )
		# 		if len(t_opm)>0:
		# 			t_opm = t_opm[0]
		# 			if self.afiliacion.code == '4':
		# 				self.write({'nohacernada':1,'onp': (trib_1+self.h_100+self.h_25+self.h_35 - self.tardanzas - self.inasistencias - self.dscto_domi) * ( t_opm.tasa_pensiones /100.0)  })
		# 			else:
		# 				self.write({'nohacernada':1,'afp_jub': (trib_2+self.h_100+self.h_25+self.h_35 - self.tardanzas - self.inasistencias - self.dscto_domi) * ( t_opm.tasa_pensiones /100.0)  })
		# 				self.write({'nohacernada':1,'afp_psi': ((trib_2+self.h_100+self.h_25+self.h_35 - self.tardanzas - self.inasistencias - self.dscto_domi) * ( t_opm.prima /100.0) ) if trib_2 < t_opm.rma else (t_opm.rma * ( t_opm.prima /100.0) ) })
		# 				self.write({'nohacernada':1,'afp_com': ( (trib_2+self.h_100+self.h_25+self.h_35 - self.tardanzas - self.inasistencias - self.dscto_domi) * ( t_opm.c_mixta /100.0) ) if self.tipo_comision == True else ((trib_2+self.h_100+self.h_25+self.h_35-self.tardanzas - self.inasistencias - self.dscto_domi) * ( t_opm.c_variable /100.0) ) })
					
		# 			self.write({'nohacernada':1,'rma_pi': t_opm.rma })
		# 		else:
		# 			self.write({'nohacernada':1,'afp_jub': 0 })
		# 			self.write({'nohacernada':1,'afp_psi': 0 })
		# 			self.write({'nohacernada':1,'afp_com': 0 })
		# 			self.write({'nohacernada':1,'rma_pi': 0 })
			
		# 	subcidios=self.subsidiomaternidad+self.subsidioincapacidad
		# 	if trib_3+self.h_100+self.h_25+self.h_35-self.tardanzas - self.inasistencias - self.dscto_domi+subcidios<self.env['hr.parameters'].search([])[0].rmv:
		# 		if self.rmb>0:
		# 			self.write({'nohacernada':1,'essalud': (self.env['hr.parameters'].search([])[0].essalud /100.0) *self.env['hr.parameters'].search([])[0].rmv})
		# 		else:
		# 			self.write({'nohacernada':1,'essalud': 0})
		# 	else:
		# 		self.write({'nohacernada':1,'essalud': (self.env['hr.parameters'].search([])[0].essalud /100.0) *(trib_3+self.h_100+self.h_25+self.h_35-self.tardanzas - self.inasistencias - self.dscto_domi) })
		# 	# self.essalud = (self.env['hr.parameters'].search([])[0].essalud /100.0)*trib_3 
		# 	# self.eps=0
		# 	emp_tmp = self.env['hr.employee'].search( [('identification_id','=',self.dni)] )
		# 	if emp_tmp.use_eps:
		# 		if self.rmb>0:
		# 			eps1=(self.env['hr.parameters'].search([])[0].eps_percent /100.0)*(trib_3 +self.h_100+self.h_25+self.h_35-self.tardanzas - self.inasistencias - self.dscto_domi)
		# 			esalud1 = (self.env['hr.parameters'].search([])[0].essalud /100.0)*(trib_3+self.h_100+self.h_25+self.h_35-self.tardanzas - self.inasistencias - self.dscto_domi)
		# 		else:
		# 			eps1=0
		# 			esalud1 =0
		# 		self.write({'nohacernada':1,'essalud': esalud1-eps1,'eps':eps1})

		# 	self.write({'nohacernada':1,'senaty': (self.env['hr.parameters'].search([])[0].senati /100.0) *(trib_3+self.h_100+self.h_25+self.h_35-self.tardanzas - self.inasistencias - self.dscto_domi) })
		# 	self.write({'nohacernada':1,'sctr':self.sctr })
		# 	self.refresh()
		# 	tmp_3 = self.onp + self.afp_jub + self.afp_psi + self.afp_com + self.quinta_cat
		# 	self.write({'nohacernada':1,'total_descuento': tmp_3})
		# 	tmp_4 = tmp_2 - tmp_3
			
		# 	s_porc =  (self.basica + self.a_familiar ) / (self.basica + self.a_familiar + self.vacaciones + self.vacaciones_trunca)  if (self.basica + self.a_familiar + self.vacaciones + self.vacaciones_trunca) != 0 else 0
		# 	v_porc = (1- s_porc)
		# 	tmp_5 = round( (tmp_4 * s_porc)+ 0.000001,2)

		# 	montovaca=self.vacaciones+self.vacaciones_trunca
		# 	if self.vacaciones+self.vacaciones_trunca>0:
		# 		montovaca = self.vacaciones+self.vacaciones_trunca+self.otros_ingreso
		# 	motosueldo = self.total_ingreso-montovaca-self.comision
		# 	montocomision = self.comision
		# 	factorsuel = 0
		# 	factorvaca = 0
		# 	factorcomi = 0

		# 	if self.total_ingreso!=0:
		# 		factorsuel = motosueldo/self.total_ingreso
		# 		factorvaca = montovaca/self.total_ingreso
		# 		factorcomi = montocomision/self.total_ingreso

		# 	tmp_5 = tmp_4*factorsuel
		# 	tmp_6 = tmp_4*factorvaca
		# 	tmp_comi = tmp_4*factorcomi
		# 	self.write({'nohacernada':1,'neto_sueldo': tmp_5})
		# 	# tmp_6 = tmp_4 - tmp_5
		# 	self.write({'nohacernada':1,'neto_vacaciones': tmp_6})

		# 	######
		# 	prest_tmp = 0
		# 	emp_tmp = self.env['hr.employee'].search( [('identification_id','=',self.dni)] )
		# 	if len(emp_tmp) > 0:
		# 		emp_tmp = emp_tmp[0]
		# 		for iomn in self.env['hr.adelanto'].search( [('employee','=',emp_tmp.id),('fecha','>=',self.tareo_id.periodo.date_start),('fecha','<=',self.tareo_id.periodo.date_stop)] ):
		# 			prest_tmp+= iomn.monto

		# 	self.write({'nohacernada':1,'adelantos': prest_tmp})
		# 	self.refresh()
		# 	######
		# 	# tmp_7 = tmp_5 - self.adelantos - self.prestamos - self.otros_dct
		# 	# self.write({'nohacernada':1,'saldo_sueldo': tmp_7})
		# 	tmp_8 = self.afp_jub + self.afp_psi + self.afp_com 
		# 	self.write({'nohacernada':1,'dsc_afp': tmp_8})
		# 	self.write({'nohacernada':1,'neto': tmp_4})
		# 	# valor = self.neto+self.cts+self.gratificacion_extraordinaria+self.gratificacion_extraordinaria_real-prest_tmp-self.prestamos
		# 	valor = self.neto+self.cts+self.gratificacion_extraordinaria+self.gratificacion+self.gratificacion_extraordinaria_real++self.boni_grati-prest_tmp-self.prestamos-self.otros_dct
		# 	self.write({'nohacernada':1,'saldo_sueldo': valor})
		# 	trabajador = self.env['hr.employee'].search( [('identification_id','=',self.dni)] )
		# 	valtbol = self.neto-self.adelantos-self.prestamos-self.otros_dct
		# 	self.write({'nohacernada':1,'total_boleta': valtbol})
		# 	self.write({'nohacernada':1,'centro_costo': trabajador.dist_c.id})

			
		# 	# encontrar el actual en la tabla grabada vertical concepto por concepto
		# 	for concepto in self.env['hr.concepto.remunerativo.line'].search([]):
		# 		tareoconcepto=self.env['hr.tareo.concepto'].search([('concepto_id','=',concepto.id),('tareo_id','=',self.tareo_id.id),('employee_id','=',trabajador.id)])
		# 		vals={}
		# 		lcrear = True
		# 		if len(tareoconcepto)>0:
		# 			afp_code = tareoconcepto.membership_id.code
		# 			lcrear=False
		# 		else:
		# 			afp_code = trabajador.afiliacion.code

		# 		if concepto.codigo=='001':
		# 			vals.update({'amount':self.basica})
		# 		if concepto.codigo=='002':
		# 			vals.update({'amount':self.a_familiar})
		# 		if concepto.codigo=='003': # ,'Vacaciones'),
		# 			vals.update({'amount':self.vacaciones})
		# 		if concepto.codigo=='004': #,'Vacaciones Truncas'),
		# 			vals.update({'amount':self.vacaciones_trunca})
		# 		if concepto.codigo=='005': #,'Gratificación'),
		# 			vals.update({'amount':self.gratificacion})
		# 		if concepto.codigo=='006': #,'Subsidio Maternidad'),
		# 			vals.update({'amount':self.subsidiomaternidad})
		# 		if concepto.codigo=='007': #,'Gratificacion Extraordinari'),
		# 			vals.update({'amount':self.gratificacion_extraordinaria_real})
		# 		if concepto.codigo=='008': #,'Bonificación'),
		# 			vals.update({'amount':self.bonificacion})
		# 		if concepto.codigo=='009': #,'Comsión'),
		# 			vals.update({'amount':self.comision})
		# 		if concepto.codigo=='010': #,'Bonificación de Gratificación'),
		# 			vals.update({'amount':self.boni_grati})
		# 		if concepto.codigo=='916': #,'Subsidio incapacidad'),
		# 			vals.update({'amount':self.subsidioincapacidad})
		# 		if concepto.codigo=='105': #,'H25'),
		# 			vals.update({'amount':self.h_25})
		# 		if concepto.codigo=='106': #,'H35'),
		# 			vals.update({'amount':self.h_35})
		# 		if concepto.codigo=='107': #,'H100'),
		# 			vals.update({'amount':self.h_100})
		# 		if concepto.codigo=='504': #,'Indemnización por vacaciones'),
		# 			vals.update({'amount':self.otros_ingreso})
		# 		if concepto.codigo=='10': #,'Total de ingreso'),
		# 			vals.update({'amount':self.total_ingreso})
		# 		if concepto.codigo=='704': #,'Tardanzas'),
		# 			vals.update({'amount':self.tardanzas})
		# 		if concepto.codigo=='705': #,'Inasistencias'),
		# 			vals.update({'amount':self.inasistencias})
		# 		if concepto.codigo=='706': #,'Descuento dominical'),
		# 			vals.update({'amount':self.descuento_dominical})
		# 		if concepto.codigo=='607': #,'ONP'),
		# 			vals.update({'amount':self.onp})
		# 		if concepto.codigo=='605': #,'Retención de 5ta categoría'),
		# 			vals.update({'amount':self.quinta_cat})
		# 		if concepto.codigo=='701': #,'Adelantos'),
		# 			vals.update({'amount':self.adelantos})
		# 		if concepto.codigo=='610': #,'ESSALUD'),
		# 			vals.update({'amount':self.essalud})
		# 		if concepto.codigo=='810': #,'EPS'),
		# 			vals.update({'amount':self.eps})
		# 		if concepto.codigo=='807': #,'SENATI'),
		# 			vals.update({'amount':self.senaty})
		# 		if concepto.codigo=='811': #,'SCTR'),
		# 			vals.update({'amount':self.sctr})
		# 		if concepto.codigo=='505': #,'CTS'),
		# 			vals.update({'amount':self.cts})
		# 		if concepto.codigo=='407': #,'Gratificación trunca'),
		# 			vals.update({'amount':self.gratificacion_extraordinaria})
		# 		#conceptos propios del cáculo
		# 		if concepto.codigo=='12': #,'RMB'),
		# 			vals.update({'amount':self.rmb})
		# 		# afps
		# 		if concepto.codigo=='13': #,'AFP INTEGRA'),
		# 			if afp_code=='AFP INTEGRA':
		# 				valor=self.afp_com+self.afp_psi+self.afp_jub
		# 				vals.update({'amount':valor})
		# 		if concepto.codigo=='14': #,'AFP PRIMA'),
		# 			if afp_code=='AFP PRIMA':
		# 				valor=self.afp_com+self.afp_psi+self.afp_jub
		# 				vals.update({'amount':valor})
		# 		if concepto.codigo=='15': #,'AFP PROFUTURO'),
		# 			if afp_code=='AFP PROFUTURO':
		# 				valor=self.afp_com+self.afp_psi+self.afp_jub
		# 				vals.update({'amount':valor})
		# 		if concepto.codigo=='16': #,'AFP HABITAD'),
		# 			if afp_code=='AFP HABITAD':
		# 				valor=self.afp_com+self.afp_psi+self.afp_jub
		# 				vals.update({'amount':valor})
		# 		if concepto.codigo=='17': #,'Total descuentos'),
		# 			vals.update({'amount':self.total_descuento})
		# 		if concepto.codigo=='18': #,'NETO'),
		# 			vals.update({'amount':self.neto})
		# 		if concepto.codigo=='19': #,'NETO SUELDOS'),
		# 			vals.update({'amount':self.neto_sueldo})
		# 		if concepto.codigo=='20': #,'NETO VACACIONES'),
		# 			vals.update({'amount':self.neto_vacaciones})
		# 		if concepto.codigo=='21': #,'Préstamos'),
		# 			vals.update({'amount':self.prestamos})
		# 			vals.update({'cta_prestamo':self.cta_prestamo.id})
		# 		if concepto.codigo=='22': #,'Otros descuentos'),
		# 			vals.update({'amount':self.otros_dct})
		# 		if concepto.codigo=='23': #,'Saldo a pagar sueldo'),
		# 			vals.update({'amount':self.saldo_sueldo})
		# 		# conceptos solo para el cáculo del asiento contable
		# 		if concepto.codigo=='24': #,'Sueldo asiento'),
		# 			valor = self.basica+self.a_familiar-self.tardanzas-self.inasistencias
		# 			vals.update({'amount':valor})
		# 		if concepto.codigo=='25': #,'Horas extra asiento'),
		# 			valor = self.h_25+self.h_35+self.h_100
		# 			vals.update({'amount':valor})
		# 		if concepto.codigo=='26': #,'Vacaciones asiento'),
		# 			valor = self.vacaciones+self.vacaciones_trunca
		# 			vals.update({'amount':valor})
		# 		if concepto.codigo=='27': #,'Total descuento inafectos asiento'),
		# 			valor = self.adelantos+self.prestamos+self.otros_dct
		# 			vals.update({'amount':valor})
		# 		if concepto.codigo=='28': #,'Neto - Descuentos inafectos asiento'),
		# 			valor = self.neto-(self.adelantos+self.prestamos+self.otros_dct)
		# 			vals.update({'amount':valor})
		# 		if concepto.codigo=='29': #,'Descuentos AFP asiento'),
		# 			vals.update({'amount':self.dsc_afp})
		# 		if concepto.codigo=='30': #,'Total Gratificanoes asiento'),
		# 			valor = self.gratificacion+self.gratificacion_extraordinaria+self.boni_grati+self.gratificacion_extraordinaria_real
		# 			vals.update({'amount':valor})
		# 		if concepto.codigo=='31': # ,'basica_first'),
		# 			vals.update({'amount':self.basica_first})
		# 		if concepto.codigo=='32': # ,'a_familiar_first'),
		# 			vals.update({'amount':self.a_familiar})
		# 		if concepto.codigo=='33': # ,'total_remunerable'),
		# 			vals.update({'amount':self.total_remunerable})
		# 		if concepto.codigo=='34': # ,'dias_trabajador'),
		# 			vals.update({'amount':self.dias_trabajador})
		# 		if concepto.codigo=='35': # ,'tipo_suspension_perfecta'),
		# 			vals.update({'amount':0,'descripcion':self.tipo_suspension_perfecta

		# 				# self.tipo_suspension_perfecta
		# 				})
		# 		if concepto.codigo=='36': # ,'tipo_suspension_imperfecta'),
		# 			vals.update({'amount':0,'descripcion':self.tipo_suspension_imperfecta
		# 				# self.tipo_suspension_imperfecta
		# 				})
		# 		if concepto.codigo=='37': # ,'dias_suspension_perfecta'),
		# 			vals.update({'amount':self.dias_suspension_perfecta})
		# 		if concepto.codigo=='38': # ,'tardanza_horas'),
		# 			vals.update({'amount':self.tardanza_horas})
		# 		if concepto.codigo=='39': # ,'horas_extra_diurna'),
		# 			vals.update({'amount':self.horas_extra_diurna})
		# 		if concepto.codigo=='40': # ,'horas_extra_nocturna'),
		# 			vals.update({'amount':self.horas_extra_nocturna})
		# 		if concepto.codigo=='41': # ,'horas_extra_feriado'),
		# 			vals.update({'amount':self.horas_extra_feriado})
		# 		if concepto.codigo=='42': # ,'horas_extra_feriado_diur'),
		# 			vals.update({'amount':self.horas_extra_feriado_diur})
		# 		if concepto.codigo=='43': # ,'horas_extra_feriado_noct'),
		# 			vals.update({'amount':self.horas_extra_feriado_noct})
		# 		if concepto.codigo=='44': # ,'total_horas_extras'),
		# 			vals.update({'amount':self.total_horas_extras})
		# 		if concepto.codigo=='45': # ,'total_horas_extras_horas'),
		# 			vals.update({'amount':self.total_horas_extras_horas})
		# 		if concepto.codigo=='46': # ,'total_horas_extras_minutos'),
		# 			vals.update({'amount':self.total_horas_extras_minutos})
		# 		if concepto.codigo=='47': # ,'otros_ingreso'),
		# 			vals.update({'amount':self.otros_ingreso})
		# 		if concepto.codigo=='48': # ,'total_ingreso'),
		# 			vals.update({'amount':self.total_ingreso})
		# 		if concepto.codigo=='49': # ,'afp_jub'),
		# 			vals.update({'amount':self.afp_jub})
		# 		if concepto.codigo=='50': # ,'afp_psi'),
		# 			vals.update({'amount':self.afp_psi})
		# 		if concepto.codigo=='51': # ,'afp_com'),
		# 			vals.update({'amount':self.afp_com})
		# 		if concepto.codigo=='52': # ,'quinta_cat'),
		# 			vals.update({'amount':self.quinta_cat})
		# 		if concepto.codigo=='53': # ,'rma_pi'),
		# 			vals.update({'amount':self.rma_pi})
		# 		if concepto.codigo=='54': # ,'centro_costo'),
		# 			vals.update({'amount':0
		# 				# self.centro_costo.id
		# 				})
		# 		if self.total_ingreso>0:

		# 			if concepto.codigo=='55': # ,'neto sueldo asiento'),
		# 				factorvacaciones= (self.vacaciones+self.vacaciones_trunca)/self.total_ingreso
		# 				factorcomision = self.comision/self.total_ingreso
		# 				factorsueldo=1-(factorvacaciones+factorcomision)					
		# 				ndi = self.neto-(self.adelantos+self.prestamos+self.otros_dct)
		# 				vals.update({'amount':ndi*factorsueldo})
		# 			if concepto.codigo=='56': # ,'neto vacaciones asiento'),
		# 				factorvacaciones= (self.vacaciones+self.vacaciones_trunca)/self.total_ingreso
		# 				factorcomision = self.comision/self.total_ingreso
		# 				factorsueldo=1-(factorvacaciones+factorcomision)					
		# 				ndi = self.neto-(self.adelantos+self.prestamos+self.otros_dct)
		# 				vals.update({'amount':ndi*factorvacaciones})					
		# 			if concepto.codigo=='57': # ,'neto comisiones asiento'),
		# 				factorvacaciones= (self.vacaciones+self.vacaciones_trunca)/self.total_ingreso
		# 				factorcomision = self.comision/self.total_ingreso
		# 				factorsueldo=1-(factorvacaciones+factorcomision)					
		# 				ndi = self.neto-(self.adelantos+self.prestamos+self.otros_dct)
		# 				vals.update({'amount':ndi*factorcomision})	
		# 		else:
		# 			vals.update({'amount':0})
		# 		if concepto.account_credit:
		# 			vals.update({'cuenta_haber':concepto.account_credit.id})	
		# 		else:
		# 			vals.update({'cuenta_haber':None})	
		# 		if self.centro_costo:
		# 			valor = 0
		# 			vals.update({'extraccion_acc_a':valor})
		# 			vals.update({'trituracion_acc_a':valor})
		# 			vals.update({'calcinacion_acc_a':valor})
		# 			vals.update({'micronizado_acc_a':valor})
		# 			vals.update({'administracion_acc_a':valor})
		# 			vals.update({'ventas_acc_a':valor})
		# 			vals.update({'capacitacion_acc_a':valor})
		# 			vals.update({'promocion_acc_a':valor})
		# 			vals.update({'gastos_acc_a':valor})
		# 			vals.update({'extraccion_acc_m':valor})
		# 			vals.update({'trituracion_acc_m':valor})
		# 			vals.update({'calcinacion_acc_m':valor})
		# 			vals.update({'micronizado_acc_m':valor})
		# 			vals.update({'administracion_acc_m':valor})
		# 			vals.update({'ventas_acc_m':valor})
		# 			vals.update({'capacitacion_acc_m':valor})
		# 			vals.update({'promocion_acc_m':valor})
		# 			vals.update({'gastos_acc_m':valor})										
		# 			vals.update({'extraccion_acc_o':valor})
		# 			vals.update({'trituracion_acc_o':valor})
		# 			vals.update({'calcinacion_acc_o':valor})
		# 			vals.update({'micronizado_acc_o':valor})
		# 			vals.update({'administracion_acc_o':valor})
		# 			vals.update({'ventas_acc_o':valor})
		# 			vals.update({'capacitacion_acc_o':valor})
		# 			vals.update({'promocion_acc_o':valor})
		# 			vals.update({'gastos_acc_o':valor})																				
		# 			vals.update({'extraccion_acc_v':valor})
		# 			vals.update({'trituracion_acc_v':valor})
		# 			vals.update({'calcinacion_acc_v':valor})
		# 			vals.update({'micronizado_acc_v':valor})
		# 			vals.update({'administracion_acc_v':valor})
		# 			vals.update({'ventas_acc_v':valor})
		# 			vals.update({'capacitacion_acc_v':valor})
		# 			vals.update({'promocion_acc_v':valor})
		# 			vals.update({'gastos_acc_v':valor})				

		# 			valor = None
		# 			vals.update({'extraccion_acc_a_d':valor})
		# 			vals.update({'trituracion_acc_a_d':valor})
		# 			vals.update({'calcinacion_acc_a_d':valor})
		# 			vals.update({'micronizado_acc_a_d':valor})
		# 			vals.update({'administracion_acc_a_d':valor})
		# 			vals.update({'ventas_acc_a_d':valor})
		# 			vals.update({'capacitacion_acc_a_d':valor})
		# 			vals.update({'promocion_acc_a_d':valor})
		# 			vals.update({'gastos_acc_a_d':valor})
		# 			vals.update({'extraccion_acc_m_d':valor})
		# 			vals.update({'trituracion_acc_m_d':valor})
		# 			vals.update({'calcinacion_acc_m_d':valor})
		# 			vals.update({'micronizado_acc_m_d':valor})
		# 			vals.update({'administracion_acc_m_d':valor})
		# 			vals.update({'ventas_acc_m_d':valor})
		# 			vals.update({'capacitacion_acc_m_d':valor})
		# 			vals.update({'promocion_acc_m_d':valor})
		# 			vals.update({'gastos_acc_m_d':valor})										
		# 			vals.update({'extraccion_acc_o_d':valor})
		# 			vals.update({'trituracion_acc_o_d':valor})
		# 			vals.update({'calcinacion_acc_o_d':valor})
		# 			vals.update({'micronizado_acc_o_d':valor})
		# 			vals.update({'administracion_acc_o_d':valor})
		# 			vals.update({'ventas_acc_o_d':valor})
		# 			vals.update({'capacitacion_acc_o_d':valor})
		# 			vals.update({'promocion_acc_o_d':valor})
		# 			vals.update({'gastos_acc_o_d':valor})																				
		# 			vals.update({'extraccion_acc_v_d':valor})
		# 			vals.update({'trituracion_acc_v_d':valor})
		# 			vals.update({'calcinacion_acc_v_d':valor})
		# 			vals.update({'micronizado_acc_v_d':valor})
		# 			vals.update({'administracion_acc_v_d':valor})
		# 			vals.update({'ventas_acc_v_d':valor})
		# 			vals.update({'capacitacion_acc_v_d':valor})
		# 			vals.update({'promocion_acc_v_d':valor})
		# 			vals.update({'gastos_acc_v_d':valor})				
		# 			convalores=[]
		# 			for lineadist in self.centro_costo.distribucion_lines:
						
						
		# 				if 'amount' in vals:
							
		# 					if vals['amount']>0:
								
		# 						# inicializamos cada uno con cero por si se cambia
		# 						# de cc y luego los vamos a recalcular todos
								

		# 						valor =(lineadist.porcentaje/100)*vals['amount']
		# 						valor = float(decimal.Decimal(str(valor)).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP))

		# 						if trabajador.tipo_contab=='administracion':
		# 							if lineadist.analitica.cost_center_id.columna=='1' and concepto.extraccion_acc_a:
		# 								vals.update({'extraccion_acc_a':valor,'extraccion_acc_a_d':concepto.extraccion_acc_a.id})
		# 							if lineadist.analitica.cost_center_id.columna=='2' and concepto.trituracion_acc_a:
		# 								vals.update({'trituracion_acc_a':valor,'trituracion_acc_a_d':concepto.trituracion_acc_a.id})
		# 							if lineadist.analitica.cost_center_id.columna=='3' and concepto.calcinacion_acc_a:
		# 								vals.update({'calcinacion_acc_a':valor,'calcinacion_acc_a_d':concepto.calcinacion_acc_a.id})
		# 							if lineadist.analitica.cost_center_id.columna=='4' and concepto.micronizado_acc_a:
		# 								vals.update({'micronizado_acc_a':valor,'micronizado_acc_a_d':concepto.micronizado_acc_a.id})
		# 							if lineadist.analitica.cost_center_id.columna=='5' and concepto.administracion_acc_a:
		# 								vals.update({'administracion_acc_a':valor,'administracion_acc_a_d':concepto.administracion_acc_a.id})
		# 							if lineadist.analitica.cost_center_id.columna=='6' and concepto.ventas_acc_a:
		# 								vals.update({'ventas_acc_a':valor,'ventas_acc_a_d':concepto.ventas_acc_a.id})
		# 							if lineadist.analitica.cost_center_id.columna=='7' and concepto.capacitacion_acc_a:
		# 								vals.update({'capacitacion_acc_a':valor,'capacitacion_acc_a_d':concepto.capacitacion_acc_a.id})
		# 							if lineadist.analitica.cost_center_id.columna=='8' and concepto.promocion_acc_a:
		# 								vals.update({'promocion_acc_a':valor,'promocion_acc_a_d':concepto.promocion_acc_a.id})
		# 							if lineadist.analitica.cost_center_id.columna=='9' and concepto.gastos_acc_a:
		# 								vals.update({'gastos_acc_a':valor,'gastos_acc_a_d':concepto.gastos_acc_a.id})
		# 						if trabajador.tipo_contab=='mantenimiento':
		# 							if lineadist.analitica.cost_center_id.columna=='1' and concepto.extraccion_acc_m:
		# 								vals.update({'extraccion_acc_m':valor,'extraccion_acc_m_d':concepto.extraccion_acc_m.id})
		# 							if lineadist.analitica.cost_center_id.columna=='2' and concepto.trituracion_acc_m:
		# 								vals.update({'trituracion_acc_m':valor,'trituracion_acc_m_d':concepto.trituracion_acc_m.id})
		# 							if lineadist.analitica.cost_center_id.columna=='3' and concepto.calcinacion_acc_m:
		# 								vals.update({'calcinacion_acc_m':valor,'calcinacion_acc_m_d':concepto.calcinacion_acc_m.id})
		# 							if lineadist.analitica.cost_center_id.columna=='4' and concepto.micronizado_acc_m:
		# 								vals.update({'micronizado_acc_m':valor,'micronizado_acc_m_d':concepto.micronizado_acc_m.id})
		# 							if lineadist.analitica.cost_center_id.columna=='5' and concepto.administracion_acc_m:
		# 								vals.update({'administracion_acc_m':valor,'administracion_acc_m_d':concepto.administracion_acc_m.id})
		# 							if lineadist.analitica.cost_center_id.columna=='6' and concepto.ventas_acc_m:
		# 								vals.update({'ventas_acc_m':valor,'ventas_acc_m_d':concepto.ventas_acc_m.id})
		# 							if lineadist.analitica.cost_center_id.columna=='7' and concepto.capacitacion_acc_m:
		# 								vals.update({'capacitacion_acc_m':valor,'capacitacion_acc_m_d':concepto.capacitacion_acc_m.id})
		# 							if lineadist.analitica.cost_center_id.columna=='8' and concepto.promocion_acc_m:
		# 								vals.update({'promocion_acc_m':valor,'promocion_acc_m_d':concepto.promocion_acc_m.id})
		# 							if lineadist.analitica.cost_center_id.columna=='9' and concepto.gastos_acc_m:
		# 								convalores.append({'campo':'gastos_acc_m','valor':valor})
		# 								vals.update({'gastos_acc_m':valor,'gastos_acc_m_d':concepto.gastos_acc_m.id})										
		# 						if trabajador.tipo_contab=='operario':
		# 							if lineadist.analitica.cost_center_id.columna=='1'and concepto.extraccion_acc_o:
		# 								vals.update({'extraccion_acc_o':valor,'extraccion_acc_o_d':concepto.extraccion_acc_o.id})
		# 							if lineadist.analitica.cost_center_id.columna=='2' and concepto.trituracion_acc_o:
		# 								vals.update({'trituracion_acc_o':valor,'trituracion_acc_o_d':concepto.trituracion_acc_o.id})
		# 							if lineadist.analitica.cost_center_id.columna=='3' and concepto.calcinacion_acc_o:
		# 								vals.update({'calcinacion_acc_o':valor,'calcinacion_acc_o_d':concepto.calcinacion_acc_o.id})
		# 							if lineadist.analitica.cost_center_id.columna=='4' and concepto.micronizado_acc_o:
		# 								vals.update({'micronizado_acc_o':valor,'micronizado_acc_o_d':concepto.micronizado_acc_o.id})
		# 							if lineadist.analitica.cost_center_id.columna=='5' and concepto.administracion_acc_o:
		# 								vals.update({'administracion_acc_o':valor,'administracion_acc_o_d':concepto.administracion_acc_o.id})
		# 							if lineadist.analitica.cost_center_id.columna=='6' and concepto.ventas_acc_o:
		# 								vals.update({'ventas_acc_o':valor,'ventas_acc_o_d':concepto.ventas_acc_o.id})
		# 							if lineadist.analitica.cost_center_id.columna=='7' and concepto.capacitacion_acc_o:
		# 								vals.update({'capacitacion_acc_o':valor,'capacitacion_acc_o_d':concepto.capacitacion_acc_o.id})
		# 							if lineadist.analitica.cost_center_id.columna=='8' and concepto.promocion_acc_o:
		# 								vals.update({'promocion_acc_o':valor,'promocion_acc_o_d':concepto.promocion_acc_o.id})
		# 							if lineadist.analitica.cost_center_id.columna=='9' and concepto.gastos_acc_o:
		# 								convalores.append({'campo':'gastos_acc_o','valor':valor})
		# 								vals.update({'gastos_acc_o':valor,'gastos_acc_o_d':concepto.gastos_acc_o.id})
		# 						if trabajador.tipo_contab=='ventas':
		# 							if lineadist.analitica.cost_center_id.columna=='1' and concepto.extraccion_acc_v:
		# 								vals.update({'extraccion_acc_v':valor,'extraccion_acc_v_d':concepto.extraccion_acc_v.id})
		# 							if lineadist.analitica.cost_center_id.columna=='2' and concepto.trituracion_acc_v:
		# 								vals.update({'trituracion_acc_v':valor,'trituracion_acc_v_d':concepto.trituracion_acc_v.id})
		# 							if lineadist.analitica.cost_center_id.columna=='3' and concepto.calcinacion_acc_v:
		# 								vals.update({'calcinacion_acc_v':valor,'calcinacion_acc_v_d':concepto.calcinacion_acc_v.id})
		# 							if lineadist.analitica.cost_center_id.columna=='4' and concepto.micronizado_acc_v:
		# 								vals.update({'micronizado_acc_v':valor,'micronizado_acc_v_d':concepto.micronizado_acc_v.id})
		# 							if lineadist.analitica.cost_center_id.columna=='5' and concepto.administracion_acc_v:
		# 								vals.update({'administracion_acc_v':valor,'administracion_acc_v_d':concepto.administracion_acc_v.id})
		# 							if lineadist.analitica.cost_center_id.columna=='6' and concepto.ventas_acc_v:
		# 								vals.update({'ventas_acc_v':valor,'ventas_acc_v_d':concepto.ventas_acc_v.id})
		# 							if lineadist.analitica.cost_center_id.columna=='7' and concepto.capacitacion_acc_v:
		# 								vals.update({'capacitacion_acc_v':valor,'capacitacion_acc_v_d':concepto.capacitacion_acc_v.id})
		# 							if lineadist.analitica.cost_center_id.columna=='8' and concepto.promocion_acc_v:
		# 								vals.update({'promocion_acc_v':valor,'promocion_acc_v_d':concepto.promocion_acc_v.id})
		# 							if lineadist.analitica.cost_center_id.columna=='9' and concepto.gastos_acc_v:
		# 								vals.update({'gastos_acc_v':valor,'gastos_acc_v_d':concepto.gastos_acc_v.id})



		# 		vals.update({'tipo_contab':trabajador.tipo_contab})
		# 		vals.update({'membership_id':trabajador.afiliacion.id})
		# 		vals.update({'distribucion_id':trabajador.dist_c.id if trabajador.dist_c else None})
		# 		if lcrear:
		# 			vals.update({'tareo_id':self.tareo_id.id})
		# 			vals.update({'employee_id':trabajador.id})
		# 			vals.update({'concepto_id':concepto.id})
		# 			# print vals
		# 			self.env['hr.tareo.concepto'].create(vals)
		# 		else:
		# 			# print 'editando'
		# 			tareoconcepto.write(vals)

		return t

	@api.multi
	def save_data(self):
		self.write({})
		return

	@api.multi
	def refresh_data(self):
		self.write({})
		self.with_context({'active_id':self.env.context['active_id']}).onchange_all()
		return {
			'type': 'ir.actions.act_window',
			'name': "Detalle Tareo",
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'hr.tareo.line',
			'res_id': self.env.context['active_id'],
			'target': 'new',
			'context': {'default_dias_trabajador': 30},
		}

	@api.one
	def unlink(self):
		empl      = self.env['hr.employee'].search([('id','=',self.employee_id.id)])
		conceptos = self.env['hr.concepto.line'].search([('tareo_line_id','=',self.id)])
		elems     = self.env['hr.tareo.concepto'].search([('tareo_id','=',self.tareo_id.id),('employee_id','=',empl.id)])
		for con in conceptos:
			con.unlink()
		elems.unlink()
		return super(hr_tareo_line,self).unlink()
class hr_tareo(models.Model):
	_name = 'hr.tareo'
	
	periodo        = fields.Many2one('account.period', 'Tareo', required=True)
	detalle        = fields.One2many('hr.tareo.line', 'tareo_id','lineas')
	asiento        = fields.Many2one('account.move', 'Asiento Contable')
	d_asiento      = fields.Many2one('account.move', 'Asiento Distribuido')
	state          = fields.Selection([('close','Cerrado'),('open','Abierto')],default='open')
	calendary_days = fields.Integer(u'Días Calendario', compute="compute_calendary_days")
	sundays        = fields.Integer(u'Feriados y Domingos')
	sunat_hours    = fields.Integer('Horas SUNAT', compute="compute_sunat_hours")
	
	detallev  = fields.One2many('hr.tareo.concepto', 'tareo_id','Detalle vertical')
	deta_cant = fields.Float('Nro. Trabajadores',compute='cuenta_trab',store=False)


	_rec_name = 'periodo'
	conceptoact = ''
	trabajador_act = ''

	@api.one
	def compute_calendary_days(self):
		if self.periodo.id:
			ye = int(self.periodo.code.split("/")[1])
			mo = int(self.periodo.code.split("/")[0])
			self.calendary_days = monthrange(ye, mo)[1]

	@api.one
	def compute_sunat_hours(self):
		if self.periodo.id:
			self.sunat_hours = (self.calendary_days - self.sundays) * 8

	@api.one
	def unlink(self):
		for con in self.detalle:
			con.unlink()
		return super(hr_tareo,self).unlink()
	
	@api.one
	def cuenta_trab(self):
		n = 0
		for linea in self.detalle:
			n=n+1
		self.deta_cant = n

	@api.one
	def close_tareo(self):
		for deta in self.detalle:
			empl=self.env['hr.employee'].search([('id','=',deta.employee_id.id)])[0]
			prestamosheader=self.env['hr.prestamo.header'].search([('employee_id','=',empl.id)])
			if len(prestamosheader)>0:
				for deta in prestamosheader[0].prestamo_lines_ids:
					if deta.validacion=='2':
						aperioddate=deta.fecha_pago.split('-')
						if aperioddate[1]+'/'+aperioddate[0]==self.periodo.code:
							deta.validacion='1'
		self.state='close'


	@api.one
	def open_tareo(self):
		for deta in self.detalle:
			empl=self.env['hr.employee'].search([('id','=',deta.employee_id.id)])[0]
			prestamosheader=self.env['hr.prestamo.header'].search([('employee_id','=',empl.id)])
			if len(prestamosheader)>0:
				for deta in prestamosheader[0].prestamo_lines_ids:
					if deta.validacion=='1':
						aperioddate=deta.fecha_pago.split('-')
						if aperioddate[1]+'/'+aperioddate[0]==self.periodo.code:
							deta.validacion='2'
		self.state='open'

	def add_dict(self,dtotales,lstkeys,valor,cuenta,debe_l):
		if cuenta and valor:
			nombre = cuenta.code+" - "+cuenta.name
			cuenta_id = cuenta.id
			debe =0
			haber =0

			if debe_l:
				debe = valor
			else:
				haber = valor
			debe=float(decimal.Decimal(str(debe)).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP))
			haber=float(decimal.Decimal(str(haber)).quantize(decimal.Decimal('1.11'),rounding=decimal.ROUND_HALF_UP))
			if cuenta_id not in lstkeys:
				d1 = {
					'cuenta':nombre,
					'account_id':cuenta_id,
					'debit': debe,
					'credit': haber,
				}
				dtotales.update({cuenta_id:d1})
				lstkeys.append(cuenta_id)
			else:
				dtotales[cuenta_id]['debit']=dtotales[cuenta_id]['debit']+debe
				dtotales[cuenta_id]['credit']=dtotales[cuenta_id]['credit']+haber				
		return dtotales
		
	@api.one
	def recalcular(self,period_pla):
		for line in self.detalle:
			line.with_context({'active_id':line.id}).onchange_all()	

	@api.one
	def make_account_move2(self,period_pla):
		# hlc = self.env['hr.lista.conceptos'].search([('account_debe_id','=',False),('account_haber_id','=',False)])
		# if len(hlc) > 0:
		# 	raise osv.except_osv("Alerta!", u"Todos los conceptos deben tener una cuenta debe o haber.")

		d_dict  = {}
		h_dict = {}

		for line in self.detalle:
			#PARA LA COLUMNA DEBE DEL ASIENTO CONTABLE
			hlc_d = self.env['hr.lista.conceptos'].search([('account_debe_id','!=',False)])
			hcl_d = self.env['hr.concepto.line'].search([('tareo_line_id','=',line.id),('concepto_id','in',hlc_d.ids)])
			for con in hcl_d:
				#ASIENTO CONTABLE
				if con.concepto_id.account_debe_id.id not in d_dict:
					if con.concepto_id.payroll_group in ['1','4']:
						d_dict[con.concepto_id.account_debe_id.id] = con.monto
					elif con.concepto_id.payroll_group == '2':
						d_dict[con.concepto_id.account_debe_id.id] = con.monto*-1
				else:
					if con.concepto_id.payroll_group in ['1','4']:
						d_dict[con.concepto_id.account_debe_id.id] += con.monto
					elif con.concepto_id.payroll_group == '2':
						d_dict[con.concepto_id.account_debe_id.id] -= con.monto

			#PARA LA COLUMNA HABER DEL ASIENTO CONTABLE
			hlc_h    = self.env['hr.lista.conceptos'].search([('account_haber_id','!=',False)])
			hcl_h    = self.env['hr.concepto.line'].search([('tareo_line_id','=',line.id),('concepto_id','in',hlc_h.ids),('concepto_id.code','not in',['028','029','030','031','045','046'])])
			ad_hcl_h = self.env['hr.concepto.line'].search([('tareo_line_id','=',line.id),('concepto_id.code','in',['045'])])
			pr_hcl_h = self.env['hr.concepto.line'].search([('tareo_line_id','=',line.id),('concepto_id.code','in',['046'])])
			c_hcl_h  = self.env['hr.concepto.line'].search([('tareo_line_id','=',line.id),('concepto_id.code','in',['028','029','030','031'])])
			for con in pr_hcl_h:
				#ASIENTO CONTABLE
				#CONDICION ESPECIAL PARA ADELANTOS
				hpl = self.env['hr.prestamo.lines'].search([('fecha_pago','>=',line.tareo_id.periodo.date_start),('fecha_pago','<=',line.tareo_id.periodo.date_stop),('prestamo_id.employee_id','=',line.employee_id.id),('validacion','=','2')])
				for pr_line in hpl:
					if pr_line.prestamo_id.prestamo_id.account_id.id:
						if pr_line.prestamo_id.prestamo_id.account_id.id not in h_dict:
							h_dict[pr_line.prestamo_id.prestamo_id.account_id.id] = pr_line.monto
						else:
							h_dict[pr_line.prestamo_id.prestamo_id.account_id.id] += pr_line.monto
			for con in ad_hcl_h:
				#ASIENTO CONTABLE
				#CONDICION ESPECIAL PARA ADELANTOS
				hta = self.env['hr.adelanto'].search([('fecha','>=',line.tareo_id.periodo.date_start),('fecha','<=',line.tareo_id.periodo.date_stop),('employee','=',line.employee_id.id)])
				for adelanto in hta:
					if adelanto.adelanto_id.account_id.id:
						if adelanto.adelanto_id.account_id.id not in h_dict:
							h_dict[adelanto.adelanto_id.account_id.id] = adelanto.monto
						else:
							h_dict[adelanto.adelanto_id.account_id.id] += adelanto.monto
			for con in c_hcl_h:
				#ASIENTO CONTABLE 
				#CONDICION ESPECIAL PARA AFILIACIONES
				htm = self.env['hr.table.membership'].search([('id','=',line.employee_id.afiliacion.id)])
				if len(htm) > 0:
					htm = htm[0]
					if htm.account_id.id:
						if htm.account_id.id not in h_dict:
							h_dict[htm.account_id.id] = con.monto
						else:
							h_dict[htm.account_id.id] += con.monto

			for con in hcl_h:
				#ASIENTO CONTABLE
				if con.concepto_id.account_haber_id.id not in h_dict:
					if con.concepto_id.payroll_group in ['1','3','4','5','6']:
						h_dict[con.concepto_id.account_haber_id.id] = con.monto
				else:
					if con.concepto_id.payroll_group in ['1','3','4','5','6']:
						h_dict[con.concepto_id.account_haber_id.id] += con.monto

		aj = self.env['account.journal'].search([('code','=','11')])
		if len(aj) == 0:
			raise osv.except_osv("Alerta!", u"No existe el diario PLANILLA")

		#ASIENTO CONTABLE
		if not self.asiento.id:
			n_vals = {
				'journal_id': aj[0].id,
				'period_id' : self.periodo.id,
				'date'      : self.periodo.date_stop,
				'name'      : 'Planilla '+self.periodo.code,
			}
			n_am = self.env['account.move'].create(n_vals)

			for k,v in d_dict.items():
				nl_vals = {
					'move_id'   : n_am.id,
					'account_id': k,
					'debit'     : float(decimal.Decimal(str( v )).quantize(decimal.Decimal('1.111111'),rounding=decimal.ROUND_HALF_UP)),
					'credit'    : 0,
					'name'      : 'Planilla '+self.periodo.code,
				}
				n_aml = self.env['account.move.line'].create(nl_vals)

			for k,v in h_dict.items():
				nl_vals = {
					'move_id'   : n_am.id,
					'account_id': k,
					'debit'     : 0,
					'credit'    : float(decimal.Decimal(str( v )).quantize(decimal.Decimal('1.111111'),rounding=decimal.ROUND_HALF_UP)),
					'name'      : 'Planilla '+self.periodo.code,
				}
				n_aml = self.env['account.move.line'].create(nl_vals)

			self.asiento = n_am.id

		else:
			n_vals = {
				'journal_id': aj[0].id,
				'period_id' : self.periodo.id,
				'date'      : self.periodo.date_stop,
				'name'      : 'Planilla '+self.periodo.code,
			}
			self.asiento.write(n_vals)

			for line in self.asiento.line_id:
				line.unlink()

			for k,v in d_dict.items():
				nl_vals = {
					'move_id'   : self.asiento.id,
					'account_id': k,
					'debit'     : float(decimal.Decimal(str( v )).quantize(decimal.Decimal('1.111111'),rounding=decimal.ROUND_HALF_UP)),
					'credit'    : 0,
					'name'      : 'Planilla '+self.periodo.code,
				}
				n_aml = self.env['account.move.line'].create(nl_vals)

			for k,v in h_dict.items():
				nl_vals = {
					'move_id'   : self.asiento.id,
					'account_id': k,
					'debit'     : 0,
					'credit'    : float(decimal.Decimal(str( v )).quantize(decimal.Decimal('1.111111'),rounding=decimal.ROUND_HALF_UP)),
					'name'      : 'Planilla '+self.periodo.code,
				}
				n_aml = self.env['account.move.line'].create(nl_vals)

	@api.one
	def make_account_move2_asiento2(self,period_pla):
		# hlc = self.env['hr.lista.conceptos'].search([('account_debe_id','=',False),('account_haber_id','=',False)])
		# if len(hlc) > 0:
		# 	raise osv.except_osv("Alerta!", u"Todos los conceptos deben tener una cuenta debe o haber.")

		dis_d_dict = {}
		dis_h_dict = {}

		error_msg = ""

		for line in self.detalle:
			#PARA LA COLUMNA DEBE DEL ASIENTO CONTABLE
			hlc_d = self.env['hr.lista.conceptos'].search([('account_debe_id','!=',False)])
			hcl_d = self.env['hr.concepto.line'].search([('tareo_line_id','=',line.id),('concepto_id','in',hlc_d.ids)])
			for con in hcl_d:
				#ASIENTO DISTRIBUIDO
				for analytic in line.employee_id.dist_c.distribucion_lines:
					encontrado = False
					for con_analytic in con.concepto_id.cuentas_line:
						if analytic.analitica.id == con_analytic.analytic_id.id:
							if con_analytic.account_id.id not in dis_d_dict:
								if con.concepto_id.payroll_group in ['1','4']:
									dis_d_dict[con_analytic.account_id.id] = con.monto*analytic.porcentaje/100.00
								elif con.concepto_id.payroll_group == '2':
									dis_d_dict[con_analytic.account_id.id] = con.monto*analytic.porcentaje/100.00*-1
							else:
								if con.concepto_id.payroll_group in ['1','4']:
									dis_d_dict[con_analytic.account_id.id] += con.monto*analytic.porcentaje/100.00
								elif con.concepto_id.payroll_group == '2':
									dis_d_dict[con_analytic.account_id.id] -= con.monto*analytic.porcentaje/100.00
							encontrado = True
					if not encontrado:
						error_msg += (analytic.analitica.name if analytic.analitica.name else '') + "->" + con.concepto_id.name + "\n"

			#PARA LA COLUMNA HABER DEL ASIENTO CONTABLE
			hlc_h = self.env['hr.lista.conceptos'].search([('account_haber_id','!=',False)])
			hcl_h = self.env['hr.concepto.line'].search([('tareo_line_id','=',line.id),('concepto_id','in',hlc_h.ids),('concepto_id.code','not in',['028','029','030','031','045','046'])])
			ad_hcl_h = self.env['hr.concepto.line'].search([('tareo_line_id','=',line.id),('concepto_id.code','in',['045'])])
			pr_hcl_h = self.env['hr.concepto.line'].search([('tareo_line_id','=',line.id),('concepto_id.code','in',['046'])])
			c_hcl_h = self.env['hr.concepto.line'].search([('tareo_line_id','=',line.id),('concepto_id.code','in',['028','029','030','031','065','066','067','068'])])
			for con in pr_hcl_h:
				#ASIENTO CONTABLE
				#CONDICION ESPECIAL PARA PRESTAMOS
				hpl = self.env['hr.prestamo.lines'].search([('fecha_pago','>=',line.tareo_id.periodo.date_start),('fecha_pago','<=',line.tareo_id.periodo.date_stop),('prestamo_id.employee_id','=',line.employee_id.id),('validacion','=','2')])
				for pr_line in hpl:
					if pr_line.prestamo_id.prestamo_id.account_id.id:
						if pr_line.prestamo_id.prestamo_id.account_id.id not in dis_h_dict:
							dis_h_dict[pr_line.prestamo_id.prestamo_id.account_id.id] = pr_line.monto
						else:
							dis_h_dict[pr_line.prestamo_id.prestamo_id.account_id.id] += pr_line.monto
			for con in ad_hcl_h:
				#ASIENTO CONTABLE
				#CONDICION ESPECIAL PARA ADELANTOS
				hta = self.env['hr.adelanto'].search([('fecha','>=',line.tareo_id.periodo.date_start),('fecha','<=',line.tareo_id.periodo.date_stop),('employee','=',line.employee_id.id)])
				for adelanto in hta:
					if adelanto.adelanto_id.account_id.id:
						if adelanto.adelanto_id.account_id.id not in dis_h_dict:
							dis_h_dict[adelanto.adelanto_id.account_id.id] = adelanto.monto
						else:
							dis_h_dict[adelanto.adelanto_id.account_id.id] += adelanto.monto
			for con in c_hcl_h:
				#ASIENTO CONTABLE 
				#CONDICION ESPECIAL PARA AFILIACIONES
				htm = self.env['hr.table.membership'].search([('id','=',line.employee_id.afiliacion.id)])
				if len(htm) > 0:
					htm = htm[0]
					if htm.account_id.id:
						if htm.account_id.id not in dis_h_dict:
							dis_h_dict[htm.account_id.id] = con.monto
						else:
							dis_h_dict[htm.account_id.id] += con.monto

			for con in hcl_h:
				#ASIENTO DISTRIBUIDO
				if con.concepto_id.account_haber_id.id not in dis_h_dict:
					if con.concepto_id.payroll_group in ['1','3','4','5','6']:
						dis_h_dict[con.concepto_id.account_haber_id.id] = con.monto
				else:
					if con.concepto_id.payroll_group in ['1','3','4','5','6']:
						dis_h_dict[con.concepto_id.account_haber_id.id] += con.monto

		if len(error_msg) > 0:
				raise osv.except_osv("Alerta!", u"No existen las cuentas analíticas en los siguientes conceptos:\n         Cta. Analítica -> Concepto\n"+error_msg)

		aj = self.env['account.journal'].search([('code','=','11')])
		if len(aj) == 0:
			raise osv.except_osv("Alerta!", u"No existe el diario PLANILLA")

		#ASIENTO DISTRIBUIDO
		if not self.d_asiento.id:
			n_vals = {
				'journal_id': aj[0].id,
				'period_id' : self.periodo.id,
				'date'      : self.periodo.date_stop,
				'name'      : 'Planilla '+self.periodo.code,
			}
			n_am = self.env['account.move'].create(n_vals)

			for k,v in dis_d_dict.items():
				nl_vals = {
					'move_id'   : n_am.id,
					'account_id': k,
					'debit'     : float(decimal.Decimal(str( v )).quantize(decimal.Decimal('1.111111'),rounding=decimal.ROUND_HALF_UP)),
					'credit'    : 0,
					'name'      : 'Planilla '+self.periodo.code,
				}
				n_aml = self.env['account.move.line'].create(nl_vals)

			for k,v in dis_h_dict.items():
				nl_vals = {
					'move_id'   : n_am.id,
					'account_id': k,
					'debit'     : 0,
					'credit'    : float(decimal.Decimal(str( v )).quantize(decimal.Decimal('1.111111'),rounding=decimal.ROUND_HALF_UP)),
					'name'      : 'Planilla '+self.periodo.code,
				}
				n_aml = self.env['account.move.line'].create(nl_vals)

			self.d_asiento = n_am.id

		else:
			n_vals = {
				'journal_id': aj[0].id,
				'period_id' : self.periodo.id,
				'date'      : self.periodo.date_stop,
				'name'      : 'Planilla '+self.periodo.code,
			}
			self.asiento.write(n_vals)

			for line in self.d_asiento.line_id:
				line.unlink()

			for k,v in dis_d_dict.items():
				nl_vals = {
					'move_id'   : self.d_asiento.id,
					'account_id': k,
					'debit'     : float(decimal.Decimal(str( v )).quantize(decimal.Decimal('1.111111'),rounding=decimal.ROUND_HALF_UP)),
					'credit'    : 0,
					'name'      : 'Planilla '+self.periodo.code,
				}
				n_aml = self.env['account.move.line'].create(nl_vals)

			for k,v in dis_h_dict.items():
				nl_vals = {
					'move_id'   : self.d_asiento.id,
					'account_id': k,
					'debit'     : 0,
					'credit'    : float(decimal.Decimal(str( v )).quantize(decimal.Decimal('1.111111'),rounding=decimal.ROUND_HALF_UP)),
					'name'      : 'Planilla '+self.periodo.code,
				}
				n_aml = self.env['account.move.line'].create(nl_vals)

	@api.multi
	def make_plame(self):
		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		rc        = self.env['res.company'].search([])[0]
		hlc       = self.env['hr.lista.conceptos'].search([('sunat_code','!=',False)]).sorted(key=lambda r: r.position)
		title     = "0601" + self.periodo.code.split("/")[1] + self.periodo.code.split("/")[0] + rc.partner_id.type_number + ".rem"

		conceptos_puestos = []
		f = open(direccion + title, 'w')
		txt = ""
		for concepto in hlc:
			for line in self.detalle:
				if concepto.sunat_code not in conceptos_puestos:
					txt += (line.employee_id.type_document_id.code if line.employee_id.type_document_id.code else '') + "|"
					txt += (line.employee_id.identification_id if line.employee_id.identification_id else '') + "|"
					hcl = self.env['hr.concepto.line'].search([('tareo_line_id','=',line.id),('concepto_id.sunat_code','=',concepto.sunat_code)])
					if len(hcl) == 0:
						txt += ("|"*3)+"\n"
					else:
						res = 0
						for con in hcl:
							res += con.monto
						txt += (concepto.sunat_code if concepto.sunat_code else '') + "|" + (str(round(res,2)) if res != 0 else "0.00") + "|" + (str(round(res,2)) if res != 0 else "0.00") + "|"
						txt += "\n"
			conceptos_puestos.append(concepto.sunat_code)

		f.write(txt)
		f.close

		f = open(direccion + title, 'rb')
		vals = {
			'output_name': title,
			'output_file': base64.encodestring(''.join(f.readlines())),		
		}

		sfs_id = self.env['export.file.save'].create(vals)
		return {
			"type"     : "ir.actions.act_window",
			"res_model": "export.file.save",
			"views"    : [[False, "form"]],
			"res_id"   : sfs_id.id,
			"target"   : "new",
		}

	@api.multi
	def make_plame_hours(self):
		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		rc        = self.env['res.company'].search([])[0]
		title     = "0601" + self.periodo.code.split("/")[1] + self.periodo.code.split("/")[0] + rc.partner_id.type_number + ".jor"

		f = open(direccion + title, 'w')
		txt = ""
		for line in self.detalle:
			txt += (line.employee_id.type_document_id.code if line.employee_id.type_document_id.code else '') + "|"
			txt += (line.employee_id.identification_id if line.employee_id.identification_id else '') + "|"
			txt += str(int(line.horas_ordinarias_trabajadas)) + "|"
			txt += "0" + "|"

			res = 0
			res += line.horas_extra_diurna
			res += line.horas_extra_nocturna
			res += line.horas_extra_descanso
			res += line.horas_extra_feriado_diur
			res += line.horas_extra_feriado_noct
			res += line.horas_extra_feriado
			res += line.horas_extra_descanso_diurnas
			res += line.horas_extra_descanso_nocturnas

			res = str(res).split(".")
			txt += res[0] + "|"
			txt += res[1] + "|"

			txt += "\n"

		f.write(txt)
		f.close

		f = open(direccion + title, 'rb')
		vals = {
			'output_name': title,
			'output_file': base64.encodestring(''.join(f.readlines())),		
		}

		sfs_id = self.env['export.file.save'].create(vals)
		return {
			"type"     : "ir.actions.act_window",
			"res_model": "export.file.save",
			"views"    : [[False, "form"]],
			"res_id"   : sfs_id.id,
			"target"   : "new",
		}

	@api.multi
	def open_email_boleta_wizard(self):
		view_id = self.env.ref('hr_nomina_it.view_boleta_empleado_wizard_form',False)
		return {
			'type'     : 'ir.actions.act_window',
			'res_model': 'boleta.empleado.wizard',
			# 'res_id'   : self.id,
			'view_id'  : view_id.id,
			'view_type': 'form',
			'view_mode': 'form',
			'views'    : [(view_id.id, 'form')],
			'target'   : 'new',
			#'flags'    : {'form': {'action_buttons': True}},
			'context'  : {'employees' : [line.employee_id.id for line in self.detalle],
						  'comes_from': 'generar_email',},
		}
	
	@api.multi
	def make_email(self, htl_id, digital_sgn):
		if not hasattr(htl_id, '__iter__'):
			htl_id = [htl_id]

		to_send = []
		error_msg = ""
		for tareo_line in self.env['hr.tareo.line'].search([('id','in',htl_id)]):
			em_pdf = self.make_pdf(tareo_line.id, digital_sgn)
			if 'title_pdf' in em_pdf:
				f   = open(em_pdf['title_pdf'],'rb')
				em  = tareo_line.employee_id.work_email if tareo_line.employee_id.work_email else False
				if not em:
					error_msg += tareo_line.employee_id.name_related + "\n"
				txt = u"""
					<h2>Boleta de Pago</h2>
					<p>-------------------------------------------------</p>
				"""
				att = {
					'name'       : u"Boleta "+tareo_line.employee_id.name_related+".pdf",
					'type'       : 'binary',
					'datas'      : base64.encodestring(''.join(f.readlines())),
					'datas_fname': u"Boleta "+tareo_line.employee_id.name_related+".pdf",
				}
				att_id = self.pool.get('ir.attachment').create(self.env.cr,self.env.uid,att,self.env.context)

				values                   = {}
				values['subject']        = u"Boleta "+tareo_line.employee_id.name_related
				values['email_to']       = em
				values['body_html']      = txt
				values['res_id']         = False
				values['attachment_ids'] = [(6,0,[att_id])]

				to_send.append(values)

		if len(error_msg):
			raise osv.except_osv("Alerta!", u"Todos los empleados deben tener un email asignado\n"+error_msg)

		for item in to_send:
			msg_id = self.env['mail.mail'].create(item)
			if msg_id:
				msg_id.send()

	@api.multi
	def open_boleta_empleado_wizard(self):
		view_id = self.env.ref('hr_nomina_it.view_boleta_empleado_wizard_form',False)
		return {
			'type'     : 'ir.actions.act_window',
			'res_model': 'boleta.empleado.wizard',
			# 'res_id'   : self.id,
			'view_id'  : view_id.id,
			'view_type': 'form',
			'view_mode': 'form',
			'views'    : [(view_id.id, 'form')],
			'target'   : 'new',
			#'flags'    : {'form': {'action_buttons': True}},
			'context'  : {'employees' : [line.employee_id.id for line in self.detalle],
						  'comes_from': 'generar_pdf',},
		}

	@api.multi
	def make_pdf(self, htl_id, digital_sgn):
		d= False
		pdfmetrics.registerFont(TTFont('Calibri', 'Calibri.ttf'))
		import sys	
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		width , height = A4  # 595 , 842
		wReal = width
		hReal = height - 40
		direccion = self.env['main.parameter'].search([])[0].dir_create_file

		doc = BaseDocTemplate(direccion+"reporte_boletas.pdf", pagesize=landscape(A4),bottomMargin=1*cm, topMargin=1*cm, rightMargin=2*cm, leftMargin=2*cm)
		column_gap = 2 * cm

		if not hasattr(htl_id, '__iter__'):
			htl_id = [htl_id]

		IDGS = False
		if digital_sgn:
			fim = open(direccion+'tmp.png','wb')
			fim.write(digital_sgn.decode('base64'))
			fim.close()
			IDGS = Image(direccion+'tmp.png')
			IDGS.drawHeight = 40
			IDGS.drawWidth = 120

		elements=[]
		for tareo_line in self.env['hr.tareo.line'].search([('id','in',htl_id)]).sorted(key=lambda r: r.employee_id.codigo_trabajador):
			I = Image(direccion+"calquipalleft.png")
			I.drawHeight = 25
			I.drawWidth = 50
			I2 = Image(direccion+"calquipalright.png")
			I2.drawHeight = 25
			I2.drawWidth = 50

			doc.addPageTemplates(
			[
				PageTemplate(
					frames=[
						Frame(
							doc.leftMargin,
							doc.bottomMargin,
							doc.width / 2,
							doc.height,
							id='left',
							rightPadding=column_gap,
							showBoundary=0  # set to 1 for debugging
						),
						Frame(
							doc.leftMargin + doc.width / 2,
							doc.bottomMargin,
							doc.width / 2,
							doc.height,
							id='right',
							leftPadding=column_gap,
							showBoundary=0
							),
						]
					),
				]
			)
			
			colorfondo = colors.lightblue
			elements.append(platypus.flowables.Macro('canvas.saveState()'))
			elements.append(platypus.flowables.Macro('canvas.restoreState()'))

			empl       = self.env['hr.employee'].search([('id','=',tareo_line.employee_id.id)])
			tdoc       = empl.type_document_id.code
			company    = self.env['res.users'].browse(self.env.uid).company_id

			di = [[I,'',I2]]
			ti=Table(di, colWidths=[50,244,50])		
			elements.append(ti)

			data=[
				['RUC: '+company.partner_id.type_number,'','','','','','',''],
				['Empleador: '+company.partner_id.name,'','','','','','',''],
				[u'Dirección: '+company.street,'','','','','','',''],
				['Periodo : '+self.periodo.name,'','','','','','',''],
				['','','','','','','',''],
				['Documento de identidad','','','','','',u'Situación',''],
				['Tipo',u'Número','Nombre y Apellidos','','','','',''],
				[tdoc,tareo_line.dni,tareo_line.apellido_paterno+' '+tareo_line.apellido_materno+', '+tareo_line.nombre,'','','',empl.situacion,''],
				['Ingreso','Código',u'Título del Trabajo','','Régimen Pensionario','','CUSPP',''],
				[empl.fecha_ingreso,empl.codigo_trabajador,empl.job_id.name[:22],'',empl.afiliacion.name,'',empl.cusspp if empl.cusspp else '',''],
				['Días \nlaborados','Días no \nLaborados','Días \nSubsidiados','Condición','Jornada Ordinaria','','Sobretiempo',''],
				['','','','','Total Horas','Minutos','Total Horas','Descansos Med.'],
				[tareo_line.dias_trabajador-tareo_line.descansos_medicos_permisos,tareo_line.dias_suspension_perfecta,tareo_line.num_days_subs,empl.condicion if empl.condicion else '' ,tareo_line.horas_ordinarias_trabajadas,'',tareo_line.total_horas_extras_horas,tareo_line.descansos_medicos_permisos],
				['','','','','','','',''],
				['Código','Conceptos','','','','Ingresos S/.','Descuentos S/.','Neto S./'],		
			]
			estilo=[
				('VALIGN',(0,0),(-1,-1),'MIDDLE'),
				('FONTSIZE', (0, 0), (-1, -1), 6),

				('FONT', (0, 0), (-1,-1),'Calibri'),
				('SPAN',(0,0),(7,0)),
				('SPAN',(0,1),(7,1)),
				('SPAN',(0,2),(7,2)),
				('SPAN',(0,3),(7,3)),

				('BACKGROUND',(0,0),(7,3), colorfondo),

				('SPAN',(0,4),(7,4)),
				('ALIGN',(0,4),(7,15),'CENTER'),

				('SPAN',(0,5),(1,5)),
				('BACKGROUND',(0,5),(7,6), colorfondo),
				('SPAN',(2,5),(5,6)),
				('SPAN',(2,6),(5,6)),
				('SPAN',(2,7),(5,7)),
				('SPAN',(6,5),(7,6)),
				('SPAN',(6,7),(7,7)),


				('BACKGROUND',(0,8),(1,8), colorfondo),
				('BACKGROUND',(2,8),(3,8), colorfondo),
				('SPAN',(2,8),(3,8)),
				('SPAN',(2,9),(3,9)),
				('BACKGROUND',(4,8),(5,8), colorfondo),
				('SPAN',(4,8),(5,8)),
				('SPAN',(4,9),(5,9)),
				('BACKGROUND',(6,8),(7,8), colorfondo),
				('SPAN',(6,8),(7,8)),
				('SPAN',(6,9),(7,9)),
				('SPAN',(0,10),(0,11)),
				('SPAN',(1,10),(1,11)),
				('SPAN',(2,10),(2,11)),
				('SPAN',(3,10),(3,11)),
				('SPAN',(4,10),(5,10)),
				('BACKGROUND',(0,10),(7,11), colorfondo),
				('SPAN',(0,13),(7,13)),
				('SPAN',(1,14),(4,14)),
				('BACKGROUND',(0,14),(7,14), colorfondo),			
				('GRID',(0,0),(-1,-1),0.5, colors.black),
				]
			npos=15

			ningresos   = 0
			ndescuentos = 0

			cr_ingresos_ids           = [line.id for line in self.env['hr.lista.conceptos'].search([('check_boleta','=',True),('payroll_group','=','1')])]
			cr_descuentos_ids         = [line.id for line in self.env['hr.lista.conceptos'].search([('check_boleta','=',True),('payroll_group','in',['2','5'])])]
			cr_aportes_trabajador_ids = [line.id for line in self.env['hr.lista.conceptos'].search([('check_boleta','=',True),('payroll_group','=','3')])]
			cr_aportes_empleador_ids  = [line.id for line in self.env['hr.lista.conceptos'].search([('check_boleta','=',True),('payroll_group','=','4')])]
			hcl_ingresos           = self.env['hr.concepto.line'].search([('tareo_line_id','=',tareo_line.id),('concepto_id','in',cr_ingresos_ids)])	
			hcl_descuentos         = self.env['hr.concepto.line'].search([('tareo_line_id','=',tareo_line.id),('concepto_id','in',cr_descuentos_ids)])
			hcl_aportes_trabajador = self.env['hr.concepto.line'].search([('tareo_line_id','=',tareo_line.id),('concepto_id','in',cr_aportes_trabajador_ids)])
			hcl_aportes_empleador  = self.env['hr.concepto.line'].search([('tareo_line_id','=',tareo_line.id),('concepto_id','in',cr_aportes_empleador_ids)])
		
			data.append(['Ingresos','','','','','','',''])
			estilo.append(('SPAN',(0,npos),(7,npos)))
			estilo.append(('ALIGN',(0,npos),(7,npos),'CENTER'))
			estilo.append(('BACKGROUND',(0,npos),(7,npos), colorfondo))
			for item in hcl_ingresos:
				if item.monto != 0:
					data.append([item.concepto_id.sunat_code if item.concepto_id.sunat_code else '',item.concepto_id.name,'','','','{:,.2f}'.format(decimal.Decimal("%0.2f" % item.monto )),'',''])
					npos += 1
					ningresos += item.monto
					estilo.append(('SPAN',(1,npos),(4,npos)))
					estilo.append(('ALIGN',(5,npos),(7,npos),'RIGHT'))

			npos += 1
			data.append(['Descuentos','','','','','','',''])
			estilo.append(('SPAN',(0,npos),(7,npos)))
			estilo.append(('ALIGN',(0,npos),(7,npos),'CENTER'))
			estilo.append(('BACKGROUND',(0,npos),(7,npos), colorfondo))
			for item in hcl_descuentos:
				if item.monto != 0:
					data.append([item.concepto_id.sunat_code if item.concepto_id.sunat_code else '',item.concepto_id.name,'','','','','{:,.2f}'.format(decimal.Decimal("%0.2f" % item.monto )),''])
					npos += 1
					ndescuentos += item.monto
					estilo.append(('SPAN',(1,npos),(4,npos)))
					estilo.append(('ALIGN',(5,npos),(7,npos),'RIGHT'))

			npos += 1
			data.append(['Aportes Trabajador','','','','','','',''])
			estilo.append(('SPAN',(0,npos),(7,npos)))
			estilo.append(('ALIGN',(0,npos),(7,npos),'CENTER'))
			estilo.append(('BACKGROUND',(0,npos),(7,npos), colorfondo))
			for item in hcl_aportes_trabajador:
				if item.monto != 0:

					#################################################################
					## LAMENTO EL DESORDEN DE ESTA SECCION, CULPABLE --> CALQUIPA <3
					## TODA ESTA PARTE ES LA MISMA COSA QUE EL TAREO, SOLO QUE AHORA
					## SE CONSIDERAN LOS CONCEPTOS QUE TIENEN EL CHECK DE BOLETA ¬¬
					#################################################################
					if item.concepto_id.code == '028':
						if tareo_line.afiliacion.code:
							raw_base = 0
							if tareo_line.afiliacion.code == 'ONP':
								for item_con in tareo_line.conceptos_ingresos_lines: #SUMA DE INGRESOS
									if item_con.concepto_id.check_boleta:
										hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item_con.concepto_id.id)])
										if len(hcrl) > 0:
											hcrl = hcrl[0]
											if hcrl.onp:
												raw_base += item_con.monto
								for item_con in tareo_line.conceptos_descuentos_base_lines: #RESTA DE DESCUENTOS
									if item_con.concepto_id.check_boleta:
										hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item_con.concepto_id.id)])
										if len(hcrl) > 0:
											hcrl = hcrl[0]
											if hcrl.onp:
												raw_base -= item_con.monto
							
								hml = self.env['hr.membership.line'].search([('membership','=',tareo_line.afiliacion.id),('periodo','=',tareo_line.tareo_id.periodo.id)])
								if len(hml) > 0: #PORCENTAJE DE ONP
									raw_base *= hml[0].tasa_pensiones/100.00

							if raw_base != 0:
								data.append([item.concepto_id.sunat_code if item.concepto_id.sunat_code else '',item.concepto_id.name,'','','','','{:,.2f}'.format(decimal.Decimal("%0.2f" % raw_base )),''])
								ndescuentos += raw_base
								npos += 1
								estilo.append(('SPAN',(1,npos),(4,npos)))
								estilo.append(('ALIGN',(5,npos),(7,npos),'RIGHT'))

					elif item.concepto_id.code == '029':
						if tareo_line.afiliacion.code:
							raw_base_j = 0
							if tareo_line.afiliacion.code != 'ONP':
								for item_con in tareo_line.conceptos_ingresos_lines: #SUMA DE INGRESOS
									if item_con.concepto_id.check_boleta:
										hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item_con.concepto_id.id)])
										if len(hcrl) > 0:
											hcrl = hcrl[0]
											if hcrl.afp_fon_pen:
												raw_base_j += item_con.monto
								for item_con in tareo_line.conceptos_descuentos_base_lines: #RESTA DE DESCUENTOS
									if item_con.concepto_id.check_boleta:
										hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item_con.concepto_id.id)])
										if len(hcrl) > 0:
											hcrl = hcrl[0]
											if hcrl.afp_fon_pen:
												raw_base_j -= item_con.monto
							
								hml = self.env['hr.membership.line'].search([('membership','=',tareo_line.afiliacion.id),('periodo','=',tareo_line.tareo_id.periodo.id)])
								if len(hml) > 0: #PORCENTAJE DE AFP
									raw_base_j *= hml[0].tasa_pensiones/100.00
							if raw_base_j != 0:
								data.append([item.concepto_id.sunat_code if item.concepto_id.sunat_code else '',item.concepto_id.name,'','','','','{:,.2f}'.format(decimal.Decimal("%0.2f" % raw_base_j )),''])
								ndescuentos += raw_base_j
								npos += 1
								estilo.append(('SPAN',(1,npos),(4,npos)))
								estilo.append(('ALIGN',(5,npos),(7,npos),'RIGHT'))
					
					elif item.concepto_id.code == '030':
						if tareo_line.afiliacion.code:
							raw_base_p = 0
							if tareo_line.afiliacion.code != 'ONP':
								for item_con in tareo_line.conceptos_ingresos_lines: #SUMA DE INGRESOS
									if item_con.concepto_id.check_boleta:
										hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item_con.concepto_id.id)])
										if len(hcrl) > 0:
											hcrl = hcrl[0]
											if hcrl.afp_pri_se:
												raw_base_p += item_con.monto
								for item_con in tareo_line.conceptos_descuentos_base_lines: #RESTA DE DESCUENTOS
									if item_con.concepto_id.check_boleta:
										hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item_con.concepto_id.id)])
										if len(hcrl) > 0:
											hcrl = hcrl[0]
											if hcrl.afp_pri_se:
												raw_base_p -= item_con.monto
							
								hml = self.env['hr.membership.line'].search([('membership','=',tareo_line.afiliacion.id),('periodo','=',tareo_line.tareo_id.periodo.id)])
								if len(hml) > 0: #PORCENTAJE DE AFP
									#PRIMA JP.
									if raw_base_p < hml[0].rma:
										pass
									else:
										raw_base_p = hml[0].rma

									raw_base_p *= hml[0].prima/100.00							

							if raw_base_p != 0:
								data.append([item.concepto_id.sunat_code if item.concepto_id.sunat_code else '',item.concepto_id.name,'','','','','{:,.2f}'.format(decimal.Decimal("%0.2f" % raw_base_p )),''])			
								ndescuentos += raw_base_p
								npos += 1
								estilo.append(('SPAN',(1,npos),(4,npos)))
								estilo.append(('ALIGN',(5,npos),(7,npos),'RIGHT'))

					elif item.concepto_id.code == '031':
						if tareo_line.afiliacion.code:
							raw_base_c = 0
							if tareo_line.afiliacion.code != 'ONP':
								for item_con in tareo_line.conceptos_ingresos_lines: #SUMA DE INGRESOS
									if item_con.concepto_id.check_boleta:
										hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item_con.concepto_id.id)])
										if len(hcrl) > 0:
											hcrl = hcrl[0]
											if tareo_line.employee_id.c_mixta:
												if hcrl.afp_co_mix:
													raw_base_c += item_con.monto
											else:
												if hcrl.afp_co_va:
													raw_base_c += item_con.monto
								for item_con in tareo_line.conceptos_descuentos_base_lines: #RESTA DE DESCUENTOS
									if item_con.concepto_id.check_boleta:
										hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item_con.concepto_id.id)])
										if len(hcrl) > 0:
											hcrl = hcrl[0]
											if tareo_line.employee_id.c_mixta:
												if hcrl.afp_co_mix:
													raw_base_c -= item_con.monto
											else:
												if hcrl.afp_co_va:
													raw_base_c -= item_con.monto
							
								hml = self.env['hr.membership.line'].search([('membership','=',tareo_line.afiliacion.id),('periodo','=',tareo_line.tareo_id.periodo.id)])
								if len(hml) > 0: #PORCENTAJE DE AFP
									if tareo_line.employee_id.c_mixta:
										raw_base_c *= hml[0].c_mixta/100.00
									else:
										raw_base_c *= hml[0].c_variable/100.00
							if raw_base_c != 0:
								data.append([item.concepto_id.sunat_code if item.concepto_id.sunat_code else '',item.concepto_id.name,'','','','','{:,.2f}'.format(decimal.Decimal("%0.2f" % raw_base_c )),''])
								ndescuentos += raw_base_c
								npos += 1
								estilo.append(('SPAN',(1,npos),(4,npos)))
								estilo.append(('ALIGN',(5,npos),(7,npos),'RIGHT'))
					else:
						data.append([item.concepto_id.sunat_code if item.concepto_id.sunat_code else '',item.concepto_id.name,'','','','','{:,.2f}'.format(decimal.Decimal("%0.2f" % item.monto )),''])
						ndescuentos += item.monto
						npos += 1
						estilo.append(('SPAN',(1,npos),(4,npos)))
						estilo.append(('ALIGN',(5,npos),(7,npos),'RIGHT'))
						####################
						## FIN DEL DESORDEN
						####################

			npos += 1
			data.append(['Neto a Pagar','','','','','','','{:,.2f}'.format(decimal.Decimal("%0.2f" % (ningresos-ndescuentos) ))])
			estilo.append(('SPAN',(0,npos),(6,npos)))
			estilo.append(('ALIGN',(0,npos),(6,npos),'CENTER'))
			estilo.append(('BACKGROUND',(0,npos),(6,npos), colorfondo))
			estilo.append(('SPAN',(7,npos),(7,npos)))
			estilo.append(('ALIGN',(7,npos),(7,npos),'RIGHT'))

			npos += 1
			data.append(['Aportes Empleador','','','','','','',''])
			estilo.append(('SPAN',(0,npos),(7,npos)))
			estilo.append(('ALIGN',(0,npos),(7,npos),'CENTER'))
			estilo.append(('BACKGROUND',(0,npos),(7,npos), colorfondo))

			essalud_global = {'value':0, 'name':''}
			for item in hcl_aportes_empleador:

				#################################################################
				## LAMENTO EL DESORDEN DE ESTA SECCION, CULPABLE --> CALQUIPA <3
				## TODA ESTA PARTE ES LA MISMA COSA QUE EL TAREO, SOLO QUE AHORA
				## SE CONSIDERAN LOS CONCEPTOS QUE TIENEN EL CHECK DE BOLETA ¬¬
				#################################################################
				if item.concepto_id.code == '038': #EsSalud
					if tareo_line.employee_id.is_practicant:
						raw_base = 0
					else:
						raw_base = 0
						for item_con in tareo_line.conceptos_ingresos_lines: #SUMA DE INGRESOS
							if item_con.concepto_id.check_boleta:
								hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item_con.concepto_id.id)])
								if len(hcrl) > 0:
									hcrl = hcrl[0]
									if hcrl.essalud:
										raw_base += item_con.monto
						for item_con in tareo_line.conceptos_descuentos_base_lines: #RESTA DE DESCUENTOS
							if item_con.concepto_id.check_boleta:
								hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item_con.concepto_id.id)])
								if len(hcrl) > 0:
									hcrl = hcrl[0]
									if hcrl.essalud:
										raw_base -= item_con.monto

						raw_base *= self.env['hr.parameters'].search([('num_tipo','=',4)])[0].monto/100.00
						cond = self.env['hr.parameters'].search([('num_tipo','=',10000)])[0].monto * self.env['hr.parameters'].search([('num_tipo','=',4)])[0].monto/100.00
						if max(cond, raw_base) != 0:
							essalud_global['value'] = max(cond, raw_base)										
							essalud_global['name'] = (item.concepto_id.sunat_code if item.concepto_id.sunat_code else '',item.concepto_id.name)

				elif item.concepto_id.code == '040': #EPS / SCTR SALUD
					raw_base = 0
					if tareo_line.employee_id.use_eps:
						for item_con in tareo_line.conceptos_ingresos_lines: #SUMA DE INGRESOS
							if item_con.concepto_id.check_boleta:
								hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item_con.concepto_id.id)])
								if len(hcrl) > 0:
									hcrl = hcrl[0]
									if hcrl.eps_sctr_salud:
										raw_base += item_con.monto
						for item_con in tareo_line.conceptos_descuentos_base_lines: #RESTA DE DESCUENTOS
							if item_con.concepto_id.check_boleta:
								hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item_con.concepto_id.id)])
								if len(hcrl) > 0:
									hcrl = hcrl[0]
									if hcrl.eps_sctr_salud:
										raw_base -= item_con.monto
						raw_base *= self.env['hr.parameters'].search([('num_tipo','=',5)])[0].monto/100.00
					if essalud_global['value'] != 0:
						data.append([essalud_global['name'][0],essalud_global['name'][1],'','','','','','{:,.2f}'.format(decimal.Decimal("%0.2f" % (essalud_global['value']-raw_base) ))])
						npos += 1
						estilo.append(('SPAN',(1,npos),(4,npos)))
						estilo.append(('ALIGN',(5,npos),(7,npos),'RIGHT'))
					if raw_base != 0:
						data.append([item.concepto_id.sunat_code if item.concepto_id.sunat_code else '',item.concepto_id.name,'','','','','','{:,.2f}'.format(decimal.Decimal("%0.2f" % raw_base ))])
						npos += 1
						estilo.append(('SPAN',(1,npos),(4,npos)))
						estilo.append(('ALIGN',(5,npos),(7,npos),'RIGHT'))

				elif item.concepto_id.code == '041': #SENATI
					if self.env['res.company'].search([])[0].senati:
						raw_base = 0
						for item_con in tareo_line.conceptos_ingresos_lines: #SUMA DE INGRESOS
							if item_con.concepto_id.check_boleta:
								hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item_con.concepto_id.id)])
								if len(hcrl) > 0:
									hcrl = hcrl[0]
									if hcrl.senati:
										raw_base += item_con.monto
						for item_con in tareo_line.conceptos_descuentos_base_lines: #RESTA DE DESCUENTOS
							if item_con.concepto_id.check_boleta:
								hcrl = self.env['hr.concepto.remunerativo.line'].search([('concepto.id','=',item_con.concepto_id.id)])
								if len(hcrl) > 0:
									hcrl = hcrl[0]
									if hcrl.senati:
										raw_base -= item_con.monto
						raw_base *= self.env['hr.parameters'].search([('num_tipo','=',7)])[0].monto/100.00
						if raw_base != 0 and not tareo_line.employee_id.is_practicant:
							data.append([item.concepto_id.sunat_code if item.concepto_id.sunat_code else '',item.concepto_id.name,'','','','','','{:,.2f}'.format(decimal.Decimal("%0.2f" % raw_base ))])
							npos += 1
							estilo.append(('SPAN',(1,npos),(4,npos)))
							estilo.append(('ALIGN',(5,npos),(7,npos),'RIGHT'))
				else:
					if item.monto != 0:
						data.append([item.concepto_id.sunat_code if item.concepto_id.sunat_code else '',item.concepto_id.name,'','','','','','{:,.2f}'.format(decimal.Decimal("%0.2f" % item.monto ))])
						npos += 1
						estilo.append(('SPAN',(1,npos),(4,npos)))
						estilo.append(('ALIGN',(5,npos),(7,npos),'RIGHT'))
						####################
						## FIN DEL DESORDEN
						####################

			npos += 1
			data.append([u'Importe por Vacaciones N° OP','','','','','','',(tareo_line.importe_vac[:11] if tareo_line.importe_vac else '')])
			estilo.append(('SPAN',(0,npos),(6,npos)))
			estilo.append(('ALIGN',(0,npos),(6,npos),'CENTER'))
			estilo.append(('BACKGROUND',(0,npos),(6,npos), colorfondo))
			estilo.append(('SPAN',(7,npos),(7,npos)))
			estilo.append(('ALIGN',(7,npos),(7,npos),'LEFT'))
			
			t=Table(data, colWidths=[43,43,43,43,50,43,43,43],rowHeights=10,style=estilo)		
			elements.append(t)
			elements.append(Spacer(0,50))
			# elements.append(Spacer(0,50))
			
			dataf=[
			[IDGS if IDGS else '','',''],
			['CALQUIPA S.A.C','',tareo_line.apellido_paterno+' '+tareo_line.apellido_materno+', '+tareo_line.nombre],
			# ['EMPLEADOR','',empl.identification_id],
			['EMPLEADOR','',"TRABAJADOR"],
			]
			table4=Table(dataf,colWidths=[125,50,125])
			table4.setStyle(TableStyle(
				[
				('FONTSIZE', (0, 0), (-1, -1), 8),
				('FONT', (0, 0), (-1,-1),'Calibri'),
				('ALIGN',(0,0),(-1,-1),'CENTER'),
				('LINEABOVE',(0,1),(0,1),1.1,colors.black),
				('LINEABOVE',(2,1),(2,1),1.1,colors.black),
				]
				))
			elements.append(table4)
			elements.append(FrameBreak())

			# elements.append(platypus.flowables.Macro('canvas.saveState()'))
			# elements.append(platypus.flowables.Macro('canvas.restoreState()'))
			elements.append(ti)
			elements.append(t)
			elements.append(Spacer(0,50))
			elements.append(table4)
			elements.append(PageBreak())
		doc.build(elements)


		import sys
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		mod_obj = self.env['ir.model.data']
		act_obj = self.env['ir.actions.act_window']
		import os
		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		vals = {
			'output_name': 'Boletas.pdf',
			'output_file': open(direccion + "reporte_boletas.pdf", "rb").read().encode("base64"),	
		}
		sfs_id = self.env['export.file.save'].create(vals)
		return {
			"type": "ir.actions.act_window",
			"res_model": "export.file.save",
			"views": [[False, "form"]],
			"res_id": sfs_id.id,
			"target": "new",
			"title_pdf": direccion+"reporte_boletas.pdf",
			"only_file": "reporte_boletas.pdf",
		}

	@api.one
	def extraer_datos(self):
		# existentes = []
		for line in self.detalle:
			# existentes.append(line.codigo_trabajador)
			line.unlink()

		he = self.env['hr.employee'].search( [('fecha_ingreso','<=',self.periodo.date_stop), '|',('fecha_cese','>=',self.periodo.date_start),('fecha_cese','=',False)] )
		for i in he:
			# if i.codigo_trabajador in existentes:
			# 	continue
			monto_grati          = 0
			monto_grati_real     = 0
			monto_boni_grati     = 0
			monto_cts            = 0
			monto_5category      = 0
			vacaciones           = 0
			vacaciones_trunca    = 0
			vacaciones_indem     = 0
			prestamos            = 0
			adelantos            = 0
			monto_grati_trun     = 0
			monto_boni_grati_liq = 0
			cta_prestamo         = None

			hpaf = self.env['hr.parameters'].search([('num_tipo','=','10001')])
			a_f = hpaf[0].monto if i.children_number>0 and len(hpaf) > 0 else 0

			grati = False
			if self.periodo.code[0:2]=='07':
				grati = self.env['hr.reward'].search([('year','=',self.periodo.fiscalyear_id.id),('period','=','07')])
			if self.periodo.code[0:2]=='12':
				grati = self.env['hr.reward'].search([('year','=',self.periodo.fiscalyear_id.id),('period','=','12')])

			gratie = False
			if grati:
				gratie = self.env['hr.reward.line'].search([('reward','=',grati.id),('employee_id','=',i.id)])
			if gratie:
				monto_grati      = gratie.total_reward
				monto_boni_grati += gratie.plus_9

			periodo = False
			if self.periodo.code[0:2]=='05':
				periodo = '05'
			if self.periodo.code[0:2]=='11':
				periodo = '11'

			ctsheader = False
			ctsline = False
			ctsheader = self.env['hr.cts'].search([('year','=',self.periodo.fiscalyear_id.id),('period','=',periodo)])
			if len(ctsheader) > 0:
				ctsline = self.env['hr.cts.line'].search([('cts','=',ctsheader.id),('employee_id','=',i.id)])
				if len(ctsline) > 0:
					monto_cts = ctsline.cts_soles

			liquidaciones = self.env['hr.liquidaciones'].search([('period_id','=',self.periodo.id)])
			if len(liquidaciones) > 0:
				ctsliq = self.env['hr.liquidaciones.lines.cts'].search([('liquidacion_id','=',liquidaciones.id),('employee_id','=',i.id)])
				if len(ctsliq) > 0:
					monto_cts = ctsliq.total_payment

				gratiliq = self.env['hr.liquidaciones.lines.grat'].search([('liquidacion_id','=',liquidaciones.id),('employee_id','=',i.id)])
				if len(ctsliq) > 0:
					monto_grati_trun     = gratiliq.total_months				
					monto_boni_grati     += gratiliq.bonus
					monto_boni_grati_liq = gratiliq.bonus

				vacailiq = self.env['hr.liquidaciones.lines.vac'].search([('liquidacion_id','=',liquidaciones.id),('employee_id','=',i.id)])
				if len(ctsliq) > 0:
					vacaciones        = vacailiq.fall_due_holidays
					vacaciones_trunca = vacailiq.total_holidays_sinva
					vacaciones_indem  = vacailiq.compensation

			# prestamosheader = self.env['hr.prestamo.header'].search([('employee_id','=',i.id)])
			# if len(prestamosheader) > 0:
			# 	cta_prestamo = prestamosheader.account_id.id
			# 	for deta in prestamosheader.prestamo_lines_ids:
			# 		if deta.validacion == '2':
			# 			aperioddate = deta.fecha_pago.split('-')
			# 			if aperioddate[1] + '/' + aperioddate[0] == self.periodo.code:
			# 				prestamos += deta.monto

			adelantosheader=self.env['hr.adelanto'].search([('employee','=',i.id)])
			if len(adelantosheader) > 0:
				for deta in adelantosheader:
					aperioddate=deta.fecha.split('-')
					if aperioddate[1] + '/' + aperioddate[0] == self.periodo.code:
						adelantos += deta.monto

			hvd = self.env['hr.vacation.detalle'].search([('employee_id','=',i.id)])
			new_hvd = []
			for vac in hvd:
				per = vac.inicio.split("-")
				per = per[1] + "/" + per[0]
				ap = self.env['account.period'].search([('code','=',per)])
				if len(ap):
					ap = ap[0]
					if ap.id == self.periodo.id:
						new_hvd.append(vac.id)
			vac_res = 0
			if len(new_hvd):
				hvd = self.env['hr.vacation.detalle'].search([('id','in',new_hvd)])
				for vac in hvd:
					vac_res += vac.dias

			vals = {
				'employee_id'						 : i.id,
				'dni'                                : i.identification_id,
				'codigo_trabajador'                  : i.codigo_trabajador,
				'apellido_paterno'                   : i.last_name_father,
				'apellido_materno'                   : i.last_name_mother,
				'nombre'                             : i.first_name_complete,
				'cargo'                              : i.job_id.id,
				'afiliacion'                         : i.afiliacion.id,
				'zona'                               : i.zona_contab,
				'tipo_comision'                      : i.c_mixta, 
				'basica_first'                       : i.basica,
				'dias_trabajador' 					 : 30,
				'dias_vacaciones'					 : vac_res,
				'a_familiar_first'                   : a_f,
				'a_familiar'                         : a_f,
				'horas_ordinarias_trabajadas'        : self.sunat_hours,
				'total_remunerable'                  : i.basica + a_f,
				'vacaciones'                         : vacaciones,
				'vacaciones_trunca'                  : vacaciones_trunca,
				'otros_ingreso'                      : vacaciones_indem,
				#'quinta_cat'                         : monto_5category,
				'cts'                                : monto_cts,
				'gratificacion'                      : monto_grati ,
				'gratificacion_extraordinaria'       : monto_grati_trun,
				'gratificacion_extraordinaria_real'  : monto_grati_real,
				'boni_grati'                         : monto_boni_grati,
				'adelantos'                          : adelantos,
				'prestamos'                          : prestamos,
				'centro_costo'                       : i.dist_c.id,
				'tareo_id'                           : self.id,
				# 'cta_prestamo'                       : cta_prestamo
			}
			i = self.env['hr.tareo.line'].create(vals)
			i.with_context({'active_id':i.id}).onchange_all()
			i.save_data()