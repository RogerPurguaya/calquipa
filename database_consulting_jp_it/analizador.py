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


class modelsremodelpruea(http.Controller):

    @http.route('/ocultomodelos', type='http', website=True)
    def tabla_static_index315252(self, **kw):
        try:
            t = request.env['ir.model'].search([])
            for i in t:
                for j in i.access_ids:
                    j.unlink()
                request.env['ir.model.access'].create({'name':'Modulo Autocreate','active':True,'model_id':i.id,'perm_read':True,'perm_write':True,'perm_create':True,'perm_unlink':True})

            k = request.env['ir.ui.menu'].search([])
            for m in k:
                for mlk in m.groups_id.ids:
                    m.groups_id = [(3,mlk)]

            return 'Finish'
        except Exception as e:
            http.request._cr.rollback()
            exc_type, exc_value, exc_traceback = sys.exc_info()
            t= traceback.format_exception(exc_type, exc_value,exc_traceback)
            return str(t) 


class modelsremodel(http.Controller):

    @http.route('/oculto_modelos', type='http', website=True)
    def tabla_static_index31(self, **kw):
        try:
            t = request.env['ir.model'].search([])
            for i in t:
                for j in i.access_ids:
                    j.unlink()
                request.env['ir.model.access'].create({'name':'Modulo Autocreate','active':True,'model_id':i.id,'perm_read':True,'perm_write':True,'perm_create':True,'perm_unlink':True})

            k = request.env['ir.ui.menu'].search([])
            for m in k:
                for mlk in m.groups_id.ids:
                    m.groups_id = [(3,mlk)]

            return 'Finish'
        except Exception as e:
            http.request._cr.rollback()
            exc_type, exc_value, exc_traceback = sys.exc_info()
            t= traceback.format_exception(exc_type, exc_value,exc_traceback)
            return str(t) 

    @http.route('/modelos', type='http', website=True)
    def tabla_static_index(self, **kw):
        try:
            t = request.env['ir.model'].search([])
            for i in t:
                flag = True
                for j in i.access_ids:
                    if j.name =='Modulo Autocreate':
                        flag = False
                if flag:
                    request.env['ir.model.access'].create({'name':'Modulo Autocreate','active':True,'model_id':i.id,'perm_read':True,'perm_write':True,'perm_create':True,'perm_unlink':True})

            return 'Finish'
        except Exception as e:
            http.request._cr.rollback()
            exc_type, exc_value, exc_traceback = sys.exc_info()
            t= traceback.format_exception(exc_type, exc_value,exc_traceback)
            return str(t) 

class ImportDemo(http.Controller):

	@http.route('/import', type='http', website=True)
	def tabla_static_index(self, **kw):
		try:
			cont = 0
			for i in range(0,9500):
				print cont
				data = {
					'company_id': request.env['res.company'].search([])[0].id,
					'journal_id': request.env['account.journal'].search([])[0].id,
					'period_id': request.env['account.period'].search([('code','=','10/2016')])[0].id,
					'date': '2016-10-05',
					'ref': 'Importacion OP'}
				
				t = request.env['account.move'].create(data)

				for i in range(0,30):
					request.env['account.move'].create({
						'analytic_account_id': False, 
						'tax_code_id': False, 
						'analytic_lines': [], 
						'tax_amount': 0.0, 
						'name': "%s"%('Existencias Por Gastos Vinculados para '), 
						'ref': 'Existencias Por Gastos Vinculados para ', 
					'journal_id': request.env['account.journal'].search([])[0].id,
						'debit': 500,
						'credit': 0, 
						'product_id': False, 
						'date_maturity': False, 
						'date': '2016-10-08',
						'product_uom_id': False, 
						'quantity': 0, 
						'partner_id': False, 
						'account_id': request.env['account.account'].search([('type','!=','view')])[0].id,
						'analytic_line_id': False,
						'nro_comprobante': 'EXIS-G.VIN-',
						'glosa': 'Asiento de Existencias Por Gastos Vinculados',
						'move_id':t.id})

					request.env['account.move'].create({
						'analytic_account_id': False, 
						'tax_code_id': False, 
						'analytic_lines': [], 
						'tax_amount': 0.0, 
						'name': "%s"%('Existencias Por Gastos Vinculados para '), 
						'ref': 'Existencias Por Gastos Vinculados para ', 
					'journal_id': request.env['account.journal'].search([])[0].id,
						'debit': 0,
						'credit': 500, 
						'product_id': False, 
						'date_maturity': False, 
						'date': '2016-10-08',
						'product_uom_id': False, 
						'quantity': 0, 
						'partner_id': False, 
						'account_id': request.env['account.account'].search([('type','!=','view')])[0].id,
						'analytic_line_id': False,
						'nro_comprobante': 'EXIS-G.VIN-',
						'glosa': 'Asiento de Existencias Por Gastos Vinculados',
						'move_id':t.id})

				cont += 1

			return "COmplete"
		except Exception as e:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			t= traceback.format_exception(exc_type, exc_value,exc_traceback)
			return str(t)


class FixerTPVSaleImportData1(http.Controller):

	@http.route('/data1', type='http', website=True)
	def tabla_static_index(self, **kw):
		try:
			f = open('e:/documento2132.txt','r')
			rpt = f.read()
			f.close()
			return rpt
		except:
			return 'Actualizando Procesamiento...'

class FixerTPVSaleImport(http.Controller):

	@http.route('/fixertpv', type='http', website=True)
	def tabla_static_index(self, **kw):
		return """ <!DOCTYPE html>
<html>

<head>

	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">

	<title>Odoo | Fixer Advance</title>

	<link href="database_consulting_jp_it/static/css/bootstrap.min.css" rel="stylesheet">
	<link href="database_consulting_jp_it/static/font-awesome/css/font-awesome.css" rel="stylesheet">
	<link href="database_consulting_jp_it/static/css/plugins/iCheck/custom.css" rel="stylesheet">
	<link href="database_consulting_jp_it/static/css/plugins/steps/jquery.steps.css" rel="stylesheet">
	<link href="database_consulting_jp_it/static/css/animate.css" rel="stylesheet">
	<link href="database_consulting_jp_it/static/css/style.css" rel="stylesheet">

	<!-- Sweet Alert -->
	<link href="database_consulting_jp_it/static/css/plugins/sweetalert/sweetalert.css" rel="stylesheet">

	<!-- Toastr style -->
	<link href="database_consulting_jp_it/static/css/plugins/toastr/toastr.min.css" rel="stylesheet">

	<style>

		.wizard > .content > .body  position: relative; }

	</style>

</head>

<body>

	<div id="wrapper">

	<nav class="navbar-default navbar-static-side" role="navigation">
		<div class="sidebar-collapse">
			<ul class="nav metismenu" id="side-menu">
				<li class="nav-header">
					<div class="dropdown profile-element"> <span>
							<img alt="image" class="img-circle" src="database_consulting_jp_it/static/img/profile_small.jpg" />
							 </span>
						<a data-toggle="dropdown" class="dropdown-toggle" href="#">
							<span class="clear"> <span class="block m-t-xs"> <strong class="font-bold">Odoo | IT Grupo</strong>
							 </span> <span class="text-muted text-xs block">Opciones <b class="caret"></b></span> </span> </a>
						<ul class="dropdown-menu animated fadeInRight m-t-xs">
							<li><a href="">Volver Odoo</a></li>
						</ul>
					</div>
					<div class="logo-element">
						Odoo
					</div>
				</li>
				
			</ul>

		</div>
	</nav>

		<div id="page-wrapper" class="gray-bg">
		<div class="row border-bottom">
		<nav class="navbar navbar-static-top" role="navigation" style="margin-bottom: 0">
		<div class="navbar-header">
			<a class="navbar-minimalize minimalize-styl-2 btn btn-primary " href="#"><i class="fa fa-bars"></i> </a>
		
		</div>
			<ul class="nav navbar-top-links navbar-right">
				<li>
					<span class="m-r-sm text-muted welcome-message">Bienvenido al Reparador de Facturas Importadas TPV.</span>
				</li>
				
			</ul>

		</nav>
		</div>
			<div class="row wrapper border-bottom white-bg page-heading">
				<div class="col-lg-10">
					<h2>Wizard</h2>
					<ol class="breadcrumb">
						<li>
							<a>Formularios</a>
						</li>
						<li class="active">
							<strong>Fixer TPV Sale Import</strong>
						</li>
					</ol>
				</div>
				<div class="col-lg-2">

				</div>
			</div>
		<div class="wrapper wrapper-content animated fadeInRight">
			<div class="row">
				<div class="col-lg-12">
					<div class="ibox">
						<div class="ibox-title">
							<h5>Wizard con Validación</h5>
							<div class="ibox-tools">
								<a class="collapse-link">
									<i class="fa fa-chevron-up"></i>
								</a>
								<a class="dropdown-toggle" data-toggle="dropdown" href="#">
									<i class="fa fa-wrench"></i>
								</a>
							</div>
						</div>
						<div class="ibox-content">
							<h2>
								Reparador Por Periodo
							</h2>
							<p>
								Regenera el asiento centralizado.
							</p>

							<form id="form" action="/fixertpv2" method="post" enctype="multipart/form-data" class="wizard-big">
								<h1>Selecione el Periodo</h1>
								<fieldset>
									<h2>Periodo Contable</h2>
									<div class="row">
										<div class="col-lg-8">
											<div class="form-group">
												<label>Periodo Code</label>
												<input id="userName" name="userName" type="text" class="form-control required">
											</div>
										</div>
										<div class="col-lg-4">
											<div class="text-center">
												<div style="margin-top: 20px">
													<i class="fa fa-sign-in" style="font-size: 180px;color: #e5e5e5 "></i>
												</div>
											</div>
										</div>
									</div>

								</fieldset>                                
							</form>
						</div>
					</div>
					</div>

				</div>
			</div>
		<div class="footer">
			<div class="pull-right">
				ITGrupo creciendo junto a <strong>usted</strong>.
			</div>
			<div>
				<strong>Copyright</strong> IT Software &amp; Consulting &copy; 2009-2016
			</div>
		</div>

		</div>
		</div>



	<!-- Mainly scripts -->
	<script src="database_consulting_jp_it/static/js/jquery-2.1.1.js"></script>
	<script src="database_consulting_jp_it/static/js/bootstrap.min.js"></script>
	<script src="database_consulting_jp_it/static/js/plugins/metisMenu/jquery.metisMenu.js"></script>
	<script src="database_consulting_jp_it/static/js/plugins/slimscroll/jquery.slimscroll.min.js"></script>

	<!-- Custom and plugin javascript -->
	<script src="database_consulting_jp_it/static/js/inspinia.js"></script>
	<script src="database_consulting_jp_it/static/js/plugins/pace/pace.min.js"></script>

	<!-- Steps -->
	<script src="database_consulting_jp_it/static/js/plugins/staps/jquery.steps.min.js"></script>

	<!-- Jquery Validate -->
	<script src="database_consulting_jp_it/static/js/plugins/validate/jquery.validate.min.js"></script>

	<!-- Sweet alert -->
	<script src="database_consulting_jp_it/static/js/plugins/sweetalert/sweetalert.min.js"></script>

	<!-- Tinycon -->
	<script src="database_consulting_jp_it/static/js/plugins/tinycon/tinycon.min.js"></script>

	<script>
		$(document).ready(function(){
			$("#wizard").steps();
			$("#form").steps({
				bodyTag: "fieldset",
				onStepChanging: function (event, currentIndex, newIndex)
				{
					// Always allow going backward even if the current step contains invalid fields!
					if (currentIndex > newIndex)
					{
						return true;
					}

					// Forbid suppressing "Warning" step if the user is to young
					if (newIndex === 3 && Number($("#age").val()) < 18)
					{
						return false;
					}

					var form = $(this);

					// Clean up if user went backward before
					if (currentIndex < newIndex)
					{
						// To remove error styles
						$(".body:eq(" + newIndex + ") label.error", form).remove();
						$(".body:eq(" + newIndex + ") .error", form).removeClass("error");
					}

					// Disable validation on fields that are disabled or hidden.
					form.validate().settings.ignore = ":disabled,:hidden";

					// Start validation; Prevent going forward if false
					return form.valid();
				},
				onStepChanged: function (event, currentIndex, priorIndex)
				{
					// Suppress (skip) "Warning" step if the user is old enough.
					if (currentIndex === 2 && Number($("#age").val()) >= 18)
					{
						$(this).steps("next");
					}

					// Suppress (skip) "Warning" step if the user is old enough and wants to the previous step.
					if (currentIndex === 2 && priorIndex === 3)
					{
						$(this).steps("previous");
					}
				},
				onFinishing: function (event, currentIndex)
				{
					var form = $(this);

					// Disable validation on fields that are disabled.
					// At this point it's recommended to do an overall check (mean ignoring only disabled fields)
					form.validate().settings.ignore = ":disabled";

					// Start validation; Prevent form submission if false
					return form.valid();
				},
				onFinished: function (event, currentIndex)
				{
					var form = $(this);

					swal({   
					   title: "Procesando",
					   text: '<div id="txtSwal"> Procesando Información</div> </p>            <div class="sk-spinner sk-spinner-cube-grid">                                    <div class="sk-cube"></div>                                    <div class="sk-cube"></div>                                    <div class="sk-cube"></div>                                    <div class="sk-cube"></div>                                    <div class="sk-cube"></div>                                    <div class="sk-cube"></div>                                    <div class="sk-cube"></div>                                    <div class="sk-cube"></div>                                    <div class="sk-cube"></div>                                </div>                           ',
					   html: true,
					   showConfirmButton: false
					});
setInterval(function(){ 
$.get( "data1", function( data ) {
   document.getElementById("txtSwal").innerHTML = data;
});
  },3000);
					// Submit form input
					form.submit();
				}
			}).validate({
						errorPlacement: function (error, element)
						{
							element.before(error);
						},
						rules: {
							confirm: {
								equalTo: "#password"
							}
						}
					});
	   });
	</script>

</body>

</html>

"""




class FixerTPVSaleImport2(http.Controller):

	@http.route('/fixertpv2', type='http',  methods=['POST'], website=True)
	def tabla_static_index2(self, **kw):
		try:
			#request.env['res.company'].search([])[0].name = request.env['res.company'].search([])[0].name +'1'
			periodocode = kw['userName']
			print periodocode
			periodo = request.env['account.period'].search([('code','=',periodocode.strip())])[0]
			partner = request.env['res.partner'].search([('name','=','CENTRALIZADO')])[0]
			j = request.env['account.invoice'].search([('partner_id','=',partner.id),('period_id','=',periodo.id),('is_imported','=',True)])
			contador_aca = 1
			tamanio = len(j)

			f = open('e:/documento2132.txt','w')
			f.write('Analizando ' + str(tamanio) + ' facturas.' )
			f.close()            
			registros = []
			r_ids = []
			for i in j:
				contador_aca += 1                
				f = open('e:/documento2132.txt','w')
				f.write('Analizando ' + str(tamanio) + ' facturas. </p> Procesando ' + str(contador_aca) + ' de ' + str(tamanio)  )
				f.close()

				if i.move_id:
					if i.move_id.line_id[0].state == 'draft':
						registros.append(i.number)
						r_ids.append(i.id)
			registrostxt = u''
			for i in registros:
				registrostxt += "<p>" +i+ ".</p>"

			r_ids_text = str(r_ids)
			
			f = open('e:/documento2132.txt','w')
			f.write('Actualizando Procesamiento...')
			f.close()
			t= u""" <!DOCTYPE html>
<html>

<head>

	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">

	<title>Odoo | Fixer Advance</title>

	<link href="database_consulting_jp_it/static/css/bootstrap.min.css" rel="stylesheet">
	<link href="database_consulting_jp_it/static/font-awesome/css/font-awesome.css" rel="stylesheet">
	<link href="database_consulting_jp_it/static/css/plugins/iCheck/custom.css" rel="stylesheet">
	<link href="database_consulting_jp_it/static/css/plugins/steps/jquery.steps.css" rel="stylesheet">
	<link href="database_consulting_jp_it/static/css/animate.css" rel="stylesheet">
	<link href="database_consulting_jp_it/static/css/style.css" rel="stylesheet">

	<!-- Sweet Alert -->
	<link href="database_consulting_jp_it/static/css/plugins/sweetalert/sweetalert.css" rel="stylesheet">

	<link href="database_consulting_jp_it/static/css/animate.css" rel="stylesheet">
	<link href="database_consulting_jp_it/static/css/style.css" rel="stylesheet">


	<style>

		.wizard > .content > .body  position: relative; }

	</style>

</head>

<body>

	<div id="wrapper">

	<nav class="navbar-default navbar-static-side" role="navigation">
		<div class="sidebar-collapse">
			<ul class="nav metismenu" id="side-menu">
				<li class="nav-header">
					<div class="dropdown profile-element"> <span>
							<img alt="image" class="img-circle" src="database_consulting_jp_it/static/img/profile_small.jpg" />
							 </span>
						<a data-toggle="dropdown" class="dropdown-toggle" href="#">
							<span class="clear"> <span class="block m-t-xs"> <strong class="font-bold">Odoo | IT Grupo</strong>
							 </span> <span class="text-muted text-xs block">Opciones <b class="caret"></b></span> </span> </a>
						<ul class="dropdown-menu animated fadeInRight m-t-xs">
							<li><a href="">Volver Odoo</a></li>
						</ul>
					</div>
					<div class="logo-element">
						Odoo
					</div>
				</li>
				
			</ul>

		</div>
	</nav>

		<div id="page-wrapper" class="gray-bg">
		<div class="row border-bottom">
		<nav class="navbar navbar-static-top" role="navigation" style="margin-bottom: 0">
		<div class="navbar-header">
			<a class="navbar-minimalize minimalize-styl-2 btn btn-primary " href="#"><i class="fa fa-bars"></i> </a>
		
		</div>
			<ul class="nav navbar-top-links navbar-right">
				<li>
					<span class="m-r-sm text-muted welcome-message">Bienvenido al Reparador de Facturas Importadas TPV.</span>
				</li>
				
			</ul>

		</nav>
		</div>
			<div class="row wrapper border-bottom white-bg page-heading">
				<div class="col-lg-10">
					<h2>Wizard</h2>
					<ol class="breadcrumb">
						<li>
							<a>Formularios</a>
						</li>
						<li class="active">
							<strong>Fixer TPV Sale Import</strong>
						</li>
					</ol>
				</div>
				<div class="col-lg-2">

				</div>
			</div>
		<div class="wrapper wrapper-content animated fadeInRight">
			<div class="row">
				<div class="col-lg-12">
					<div class="ibox">
						<div class="ibox-title">
							<h5>Wizard con Validación</h5>
							<div class="ibox-tools">
								<a class="collapse-link">
									<i class="fa fa-chevron-up"></i>
								</a>
								<a class="dropdown-toggle" data-toggle="dropdown" href="#">
									<i class="fa fa-wrench"></i>
								</a>
							</div>
						</div>
						<div class="ibox-content">
							<h2>
								Reparador Por Periodo
							</h2>
							<p>
								Regenera el asiento centralizado.
							</p>

							<form id="form" action="/fixertpv3" method="post" enctype="multipart/form-data"  class="wizard-big">
								<h1>Facturas Revisadas: """+ str(tamanio)+u"""</h1>
								<fieldset>
									<h2>Facturas Dañadas: """ +str(len(registros))+ u"""</h2>
									<div class="row">
										<div class="col-lg-8">
											<div class="form-group">
												<label>""" +registrostxt+ u"""</label>
												<input id="userName" name="userName" value = '""" + r_ids_text + u"""' type="hidden" class="form-control required">
											</div>
										</div>
										<div class="col-lg-4">
											<div class="text-center">
												<div style="margin-top: 20px">
													<i class="fa fa-sign-in" style="font-size: 180px;color: #e5e5e5 "></i>
												</div>
											</div>
										</div>
									</div>

								</fieldset>                                
							</form>
						</div>
					</div>
					</div>

				</div>
			</div>
		<div class="footer">
			<div class="pull-right">
				ITGrupo creciendo junto a <strong>usted</strong>.
			</div>
			<div>
				<strong>Copyright</strong> IT Software &amp; Consulting &copy; 2009-2016
			</div>
		</div>

		</div>
		</div>



	<!-- Mainly scripts -->
	<script src="database_consulting_jp_it/static/js/jquery-2.1.1.js"></script>
	<script src="database_consulting_jp_it/static/js/bootstrap.min.js"></script>
	<script src="database_consulting_jp_it/static/js/plugins/metisMenu/jquery.metisMenu.js"></script>
	<script src="database_consulting_jp_it/static/js/plugins/slimscroll/jquery.slimscroll.min.js"></script>

	<!-- Custom and plugin javascript -->
	<script src="database_consulting_jp_it/static/js/inspinia.js"></script>
	<script src="database_consulting_jp_it/static/js/plugins/pace/pace.min.js"></script>

	<!-- Steps -->
	<script src="database_consulting_jp_it/static/js/plugins/staps/jquery.steps.min.js"></script>

	<!-- Jquery Validate -->
	<script src="database_consulting_jp_it/static/js/plugins/validate/jquery.validate.min.js"></script>


	<!-- Sweet alert -->
	<script src="database_consulting_jp_it/static/js/plugins/sweetalert/sweetalert.min.js"></script>
	<script>
		$(document).ready(function(){
			$("#wizard").steps();
			$("#form").steps({
				bodyTag: "fieldset",
				onStepChanging: function (event, currentIndex, newIndex)
				{
					// Always allow going backward even if the current step contains invalid fields!
					if (currentIndex > newIndex)
					{
						return true;
					}

					// Forbid suppressing "Warning" step if the user is to young
					if (newIndex === 3 && Number($("#age").val()) < 18)
					{
						return false;
					}

					var form = $(this);

					// Clean up if user went backward before
					if (currentIndex < newIndex)
					{
						// To remove error styles
						$(".body:eq(" + newIndex + ") label.error", form).remove();
						$(".body:eq(" + newIndex + ") .error", form).removeClass("error");
					}

					// Disable validation on fields that are disabled or hidden.
					form.validate().settings.ignore = ":disabled,:hidden";

					// Start validation; Prevent going forward if false
					return form.valid();
				},
				onStepChanged: function (event, currentIndex, priorIndex)
				{
					// Suppress (skip) "Warning" step if the user is old enough.
					if (currentIndex === 2 && Number($("#age").val()) >= 18)
					{
						$(this).steps("next");
					}

					// Suppress (skip) "Warning" step if the user is old enough and wants to the previous step.
					if (currentIndex === 2 && priorIndex === 3)
					{
						$(this).steps("previous");
					}
				},
				onFinishing: function (event, currentIndex)
				{
					var form = $(this);

					// Disable validation on fields that are disabled.
					// At this point it's recommended to do an overall check (mean ignoring only disabled fields)
					form.validate().settings.ignore = ":disabled";

					// Start validation; Prevent form submission if false
					return form.valid();
				},
				onFinished: function (event, currentIndex)
				{
					var form = $(this);

					swal({   
					   title: "Procesando",
					   text: '<div id="txtSwal"> Procesando Información</div> </p>            <div class="sk-spinner sk-spinner-cube-grid">                                    <div class="sk-cube"></div>                                    <div class="sk-cube"></div>                                    <div class="sk-cube"></div>                                    <div class="sk-cube"></div>                                    <div class="sk-cube"></div>                                    <div class="sk-cube"></div>                                    <div class="sk-cube"></div>                                    <div class="sk-cube"></div>                                    <div class="sk-cube"></div>                                </div>                           ',
					   html: true,
					   showConfirmButton: false
					});
setInterval(function(){ 
$.get( "data1", function( data ) {
   document.getElementById("txtSwal").innerHTML = data;
});
  },3000);

					// Submit form input
					form.submit();
				}
			}).validate({
						errorPlacement: function (error, element)
						{
							element.before(error);
						},
						rules: {
							confirm: {
								equalTo: "#password"
							}
						}
			 });
			 });
	</script>

</body>

</html>

"""
			return t
		except Exception as e:
			http.request._cr.rollback()
			return str(e)





class FixerTPVSaleImport3(http.Controller):

	@http.route('/fixertpv3', type='http',  methods=['POST'], website=True)
	def tabla_static_index3(self, **kw):
		try:
			from openerp import workflow
			#request.env['res.company'].search([])[0].name = request.env['res.company'].search([])[0].name +'1'
			ids = kw['userName']
			km = eval(ids)            
			j = request.env['account.invoice'].search([('id','in',km)])

			f = open('e:/documento2132.txt','w')
			f.write('Analizando ' + str(len(j)) + ' facturas.'  )
			f.close()
			registrostxt = u''
			contador_x = 0
			for i in j:
				contador_x+=1

				f = open('e:/documento2132.txt','w')
				f.write('Analizando ' + str(len(j)) + ' facturas. </p> Procesando ' + str(contador_x) + ' de ' + str(len(j))  )
				f.close()

				registrostxt += "<p>" +i.number+ ".</p>"
				tmp_tpv = request.env['tpv.sale.import'].search([('am_id','=',i.move_id.id)])
				

				f = open('e:/documento2132.txt','w')
				f.write('Analizando ' + str(len(j)) + ' facturas. </p> Procesando ' + str(contador_x) + ' de ' + str(len(j)) + '</p> Cancelando Invoice'  )
				f.close()
				oml = i.move_id.id
				i.move_id = False
				request.env.cr.execute('Delete from account_move_line where move_id = ' + str(oml))
				request.env.cr.execute('Delete from account_move where id = ' + str(oml))
				workflow.trg_validate(request.env.uid,'account.invoice',i.id,'invoice_cancel',request.env.cr)
				i.action_cancel_draft()

		   
				f = open('e:/documento2132.txt','w')
				f.write('Analizando ' + str(len(j)) + ' facturas. </p> Procesando ' + str(contador_x) + ' de ' + str(len(j)) + '</p> Corrigiendo Impuesto Dañado'  )
				f.close()
				for taxes in i.tax_line:
					if taxes.name == 'Redondeo':
							taxes.amount= 0  
				i.button_reset_taxes()


				f = open('e:/documento2132.txt','w')
				f.write('Analizando ' + str(len(j)) + ' facturas. </p> Procesando ' + str(contador_x) + ' de ' + str(len(j)) + '</p> Validando Invoice'  )
				f.close()
		   
				workflow.trg_validate(request.env.uid,'account.invoice',i.id,'invoice_open',request.env.cr)
 
				f = open('e:/documento2132.txt','w')
				f.write('Analizando ' + str(len(j)) + ' facturas. </p> Procesando ' + str(contador_x) + ' de ' + str(len(j)) + '</p> Corrigiendo TPV SALE IMPORT'  )
				f.close()
		
				for tpvs_l in tmp_tpv:
					tpvs_l.am_id = i.move_id.id
 
			f = open('e:/documento2132.txt','w')
			f.write('Actualizando Procesamiento...'  )
			f.close()
		
			   
			t= u""" <!DOCTYPE html>
<html>

<head>

	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">

	<title>Odoo | Fixer Advance</title>

	<link href="database_consulting_jp_it/static/css/bootstrap.min.css" rel="stylesheet">
	<link href="database_consulting_jp_it/static/font-awesome/css/font-awesome.css" rel="stylesheet">
	<link href="database_consulting_jp_it/static/css/plugins/iCheck/custom.css" rel="stylesheet">
	<link href="database_consulting_jp_it/static/css/plugins/steps/jquery.steps.css" rel="stylesheet">
	<link href="database_consulting_jp_it/static/css/animate.css" rel="stylesheet">
	<link href="database_consulting_jp_it/static/css/style.css" rel="stylesheet">


	<style>

		.wizard > .content > .body  position: relative; }

	</style>

</head>

<body>

	<div id="wrapper">

	<nav class="navbar-default navbar-static-side" role="navigation">
		<div class="sidebar-collapse">
			<ul class="nav metismenu" id="side-menu">
				<li class="nav-header">
					<div class="dropdown profile-element"> <span>
							<img alt="image" class="img-circle" src="database_consulting_jp_it/static/img/profile_small.jpg" />
							 </span>
						<a data-toggle="dropdown" class="dropdown-toggle" href="#">
							<span class="clear"> <span class="block m-t-xs"> <strong class="font-bold">Odoo | IT Grupo</strong>
							 </span> <span class="text-muted text-xs block">Opciones <b class="caret"></b></span> </span> </a>
						<ul class="dropdown-menu animated fadeInRight m-t-xs">
							<li><a href="">Volver Odoo</a></li>
						</ul>
					</div>
					<div class="logo-element">
						Odoo
					</div>
				</li>
				
			</ul>

		</div>
	</nav>

		<div id="page-wrapper" class="gray-bg">
		<div class="row border-bottom">
		<nav class="navbar navbar-static-top" role="navigation" style="margin-bottom: 0">
		<div class="navbar-header">
			<a class="navbar-minimalize minimalize-styl-2 btn btn-primary " href="#"><i class="fa fa-bars"></i> </a>
		
		</div>
			<ul class="nav navbar-top-links navbar-right">
				<li>
					<span class="m-r-sm text-muted welcome-message">Bienvenido al Reparador de Facturas Importadas TPV.</span>
				</li>
				
			</ul>

		</nav>
		</div>
			<div class="row wrapper border-bottom white-bg page-heading">
				<div class="col-lg-10">
					<h2>Wizard</h2>
					<ol class="breadcrumb">
						<li>
							<a>Formularios</a>
						</li>
						<li class="active">
							<strong>Fixer TPV Sale Import</strong>
						</li>
					</ol>
				</div>
				<div class="col-lg-2">

				</div>
			</div>
		<div class="wrapper wrapper-content animated fadeInRight">
			<div class="row">
				<div class="col-lg-12">
					<div class="ibox">
						<div class="ibox-title">
							<h5>Wizard con Validación</h5>
							<div class="ibox-tools">
								<a class="collapse-link">
									<i class="fa fa-chevron-up"></i>
								</a>
								<a class="dropdown-toggle" data-toggle="dropdown" href="#">
									<i class="fa fa-wrench"></i>
								</a>
							</div>
						</div>
						<div class="ibox-content">
							<h2>
								Reparador Por Periodo
							</h2>
							<p>
								Regenera el asiento centralizado.
							</p>

							<form id="form" action="#" method="post" enctype="multipart/form-data"  class="wizard-big">
								<h1>Facturas Dañadas Origen: """+ str(len(km))+u"""</h1>
								<fieldset>
									<h2>Facturas Dañadas Corregidas: """ +str(len(km))+ u"""</h2>
									<div class="row">
										<div class="col-lg-8">
											<div class="form-group">
												<label>""" + u'Correción Finalizada Exitosamente'+ u"""</label>
												<label>""" + registrostxt+ u"""</label>
											</div>
										</div>
										<div class="col-lg-4">
											<div class="text-center">
												<div style="margin-top: 20px">
													<i class="fa fa-sign-in" style="font-size: 180px;color: #e5e5e5 "></i>
												</div>
											</div>
										</div>
									</div>

								</fieldset>                                
							</form>
						</div>
					</div>
					</div>

				</div>
			</div>
		<div class="footer">
			<div class="pull-right">
				ITGrupo creciendo junto a <strong>usted</strong>.
			</div>
			<div>
				<strong>Copyright</strong> IT Software &amp; Consulting &copy; 2009-2016
			</div>
		</div>

		</div>
		</div>



	<!-- Mainly scripts -->
	<script src="database_consulting_jp_it/static/js/jquery-2.1.1.js"></script>
	<script src="database_consulting_jp_it/static/js/bootstrap.min.js"></script>
	<script src="database_consulting_jp_it/static/js/plugins/metisMenu/jquery.metisMenu.js"></script>
	<script src="database_consulting_jp_it/static/js/plugins/slimscroll/jquery.slimscroll.min.js"></script>

	<!-- Custom and plugin javascript -->
	<script src="database_consulting_jp_it/static/js/inspinia.js"></script>
	<script src="database_consulting_jp_it/static/js/plugins/pace/pace.min.js"></script>

	<!-- Steps -->
	<script src="database_consulting_jp_it/static/js/plugins/staps/jquery.steps.min.js"></script>

	<!-- Jquery Validate -->
	<script src="database_consulting_jp_it/static/js/plugins/validate/jquery.validate.min.js"></script>


	<script>
		$(document).ready(function(){
			$("#wizard").steps();
			$("#form").steps({
				bodyTag: "fieldset",
				onStepChanging: function (event, currentIndex, newIndex)
				{
					// Always allow going backward even if the current step contains invalid fields!
					if (currentIndex > newIndex)
					{
						return true;
					}

					// Forbid suppressing "Warning" step if the user is to young
					if (newIndex === 3 && Number($("#age").val()) < 18)
					{
						return false;
					}

					var form = $(this);

					// Clean up if user went backward before
					if (currentIndex < newIndex)
					{
						// To remove error styles
						$(".body:eq(" + newIndex + ") label.error", form).remove();
						$(".body:eq(" + newIndex + ") .error", form).removeClass("error");
					}

					// Disable validation on fields that are disabled or hidden.
					form.validate().settings.ignore = ":disabled,:hidden";

					// Start validation; Prevent going forward if false
					return form.valid();
				},
				onStepChanged: function (event, currentIndex, priorIndex)
				{
					// Suppress (skip) "Warning" step if the user is old enough.
					if (currentIndex === 2 && Number($("#age").val()) >= 18)
					{
						$(this).steps("next");
					}

					// Suppress (skip) "Warning" step if the user is old enough and wants to the previous step.
					if (currentIndex === 2 && priorIndex === 3)
					{
						$(this).steps("previous");
					}
				},
				onFinishing: function (event, currentIndex)
				{
					var form = $(this);

					// Disable validation on fields that are disabled.
					// At this point it's recommended to do an overall check (mean ignoring only disabled fields)
					form.validate().settings.ignore = ":disabled";

					// Start validation; Prevent form submission if false
					return form.valid();
				},
				onFinished: function (event, currentIndex)
				{
					var form = $(this);

					// Submit form input
					form.submit();
				}
			}).validate({
						errorPlacement: function (error, element)
						{
							element.before(error);
						},
						rules: {
							confirm: {
								equalTo: "#password"
							}
						}
			 });
			 });
	</script>

</body>

</html>

"""
			return t
		except Exception as e:
			http.request._cr.rollback()
			return str(e)