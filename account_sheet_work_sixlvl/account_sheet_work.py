# -*- coding: utf-8 -*-

from openerp import models, fields, api


class account_sheet_work_simple_visual(models.Model):
	_name = 'account.sheet.work.simple.visual'


	clasificationactual = fields.Char('clasification',size=50)
	levelactual= fields.Char('level', size=50)
	clasification = fields.Char('clasification',size=50)
	level= fields.Char('level', size=50)
	periodo= fields.Char('Periodo', size=50)
	cuenta= fields.Char('Cuenta', size=200)
	descripcion= fields.Char('Descripción', size=200)
	debe = fields.Float('Debe', digits=(12,2))
	haber = fields.Float('Haber', digits=(12,2))
	saldodeudor = fields.Float('Saldo Deudo', digits=(12,2))
	saldoacredor = fields.Float('Saldo Acreedor', digits=(12,2))

class account_sheet_work_detalle_visual(models.Model):
	_name = 'account.sheet.work.detalle.visual'

	clasificationactual = fields.Char('clasification',size=50)
	levelactual= fields.Char('level', size=50)
	clasification = fields.Char('clasification',size=50)
	level= fields.Char('level', size=50)
	periodo= fields.Char('Periodo', size=50)
	cuenta= fields.Char('Cuenta', size=200)
	descripcion= fields.Char('Descripción', size=200)
	debe = fields.Float('Debe', digits=(12,2))
	haber = fields.Float('Haber', digits=(12,2))
	saldodeudor = fields.Float('Saldo Deudo', digits=(12,2))
	saldoacredor = fields.Float('Saldo Acreedor', digits=(12,2))
	activo = fields.Float('Activo', digits=(12,2))
	pasivo = fields.Float('Pasivo', digits=(12,2))
	perdidasnat = fields.Float('Perdidas NAT', digits=(12,2))
	ganancianat = fields.Float('Ganacias NAT', digits=(12,2))
	perdidasfun = fields.Float('Perdidas FUN', digits=(12,2))
	gananciafun = fields.Float('Ganancia FUN', digits=(12,2))



class account_sheet_work_simple(models.Model):
	_name = 'account.sheet.work.simple'
	_auto = False

	cuenta= fields.Char('Cuenta', size=200)
	descripcion= fields.Char('Descripción', size=200)
	debe = fields.Float('Debe', digits=(12,2))
	haber = fields.Float('Haber', digits=(12,2))
	saldodeudor = fields.Float('Saldo Deudo', digits=(12,2))
	saldoacredor = fields.Float('Saldo Acreedor', digits=(12,2))


class account_sheet_work_detalle(models.Model):
	_name = 'account.sheet.work.detalle'
	_auto = False


	clasificationactual = fields.Char('clasification',size=50)
	levelactual= fields.Char('level', size=50)
	clasification = fields.Char('clasification',size=50)
	level= fields.Char('level', size=50)
	periodo= fields.Char('Periodo', size=50)
	cuenta= fields.Char('Cuenta', size=200)
	cuentaactual= fields.Char('Cuenta', size=200)
	descripcion= fields.Char('Descripción', size=200)
	debe = fields.Float('Debe', digits=(12,2))
	haber = fields.Float('Haber', digits=(12,2))
	saldodeudor = fields.Float('Saldo Deudo', digits=(12,2))
	saldoacredor = fields.Float('Saldo Acreedor', digits=(12,2))
	activo = fields.Float('Activo', digits=(12,2))
	pasivo = fields.Float('Pasivo', digits=(12,2))
	perdidasnat = fields.Float('Perdidas Nat.', digits=(12,2))
	ganancianat = fields.Float('Ganancia Nat.', digits=(12,2))
	perdidasfun = fields.Float('Perdidas Fun.', digits=(12,2))
	gananciafun = fields.Float('Ganancia Fun.', digits=(12,2))

	def init(self,cr):
		cr.execute("""

drop function if exists get_hoja_trabajo_simple_six(boolean,integer,integer,integer) CASCADE;
create or replace function get_hoja_trabajo_simple_six(boolean,integer,integer,integer)
	RETURNS TABLE(id bigint, level varchar, clasificationactual varchar, cuenta text, description varchar, levelactual varchar, clasification varchar, debe numeric, haber numeric, saldodeudor numeric, saldoacredor numeric) AS
$BODY$
BEGIN

IF $3 is Null THEN
		$3 := $2;
END IF;

RETURN QUERY 
select row_number() OVER () AS id,* from (
select '0'::varchar as level,'0'::varchar as clasificationactual,CASE WHEN $4 = 8 THEN T.cuentaactual ELSE substring( T.cuentaactual, 0, $4) END as cuenta,aa.name as description, '0'::varchar as levelactual, '0'::varchar as clasification, 
sum(T.debe) as debe,
sum(T.haber) as haber,

CASE WHEN sum(T.saldodeudor) - sum(T.saldoacredor)>0 THEN  sum(T.saldodeudor) - sum(T.saldoacredor) ELSE 0 END as saldodeudor,
CASE WHEN sum(T.saldoacredor) - sum(T.saldodeudor)>0 THEN  sum(T.saldoacredor) - sum(T.saldodeudor) ELSE 0 END as saldoacredor

from get_hoja_trabajo_simple( $1,$2,$3) as T
left join account_account aa on aa.name = CASE WHEN $4 = 8 THEN T.cuentaactual ELSE substring( T.cuentaactual, 0, $4) END 
group by CASE WHEN $4 = 8 THEN T.cuentaactual ELSE substring( T.cuentaactual, 0, $4) END, aa.name 
order by CASE WHEN $4 = 8 THEN T.cuentaactual ELSE substring( T.cuentaactual, 0, $4) END
) AS T;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;



drop function if exists get_hoja_trabajo_detalle_six(boolean,integer,integer,integer) CASCADE ;
create or replace function get_hoja_trabajo_detalle_six(boolean,integer,integer,integer)
	RETURNS TABLE(id bigint, level varchar, clasificationactual varchar, cuenta text, description varchar, levelactual varchar, clasification varchar, debe numeric, haber numeric, saldodeudor numeric, saldoacredor numeric, activo numeric, pasivo numeric, perdidasnat numeric, ganancianat numeric, perdidasfun numeric, gananciafun numeric) AS
$BODY$
BEGIN

IF $3 is Null THEN
		$3 := $2;
END IF;

RETURN QUERY 
select row_number() OVER () AS id,* from (
select '0'::varchar as level,'0'::varchar as clasificationactual,CASE WHEN $4 = 8 THEN T.cuentaactual ELSE substring( T.cuentaactual, 0, $4) END as cuenta,aa.name as description, '0'::varchar as levelactual, '0'::varchar as clasification, 
sum(T.debe) as debe,
sum(T.haber) as haber,

CASE WHEN sum(T.saldodeudor) - sum(T.saldoacredor)>0 THEN  sum(T.saldodeudor) - sum(T.saldoacredor) ELSE 0 END as saldodeudor,
CASE WHEN sum(T.saldoacredor) - sum(T.saldodeudor)>0 THEN  sum(T.saldoacredor) - sum(T.saldodeudor) ELSE 0 END as saldoacredor,

CASE WHEN sum(T.activo) - sum(T.pasivo)>0 THEN  sum(T.activo) - sum(T.pasivo) ELSE 0 END as activo,
CASE WHEN sum(T.pasivo) - sum(T.activo)>0 THEN  sum(T.pasivo) - sum(T.activo) ELSE 0 END as pasivo,

CASE WHEN sum(T.perdidasnat) - sum(T.ganancianat)>0 THEN  sum(T.perdidasnat) - sum(T.ganancianat) ELSE 0 END as perdidasnat,
CASE WHEN sum(T.ganancianat) - sum(T.perdidasnat)>0 THEN  sum(T.ganancianat) - sum(T.perdidasnat) ELSE 0 END as ganancianat,


CASE WHEN sum(T.perdidasfun) - sum(T.gananciafun)>0 THEN  sum(T.perdidasfun) - sum(T.gananciafun) ELSE 0 END as perdidasfun,
CASE WHEN sum(T.gananciafun) - sum(T.perdidasfun)>0 THEN  sum(T.gananciafun) - sum(T.perdidasfun) ELSE 0 END as gananciafun

from get_hoja_trabajo_detalle( $1,$2,$3) as T
left join account_account aa on aa.name = CASE WHEN $4 = 8 THEN T.cuentaactual ELSE substring( T.cuentaactual, 0, $4) END 
group by CASE WHEN $4 = 8 THEN T.cuentaactual ELSE substring( T.cuentaactual, 0, $4) END, aa.name 
order by CASE WHEN $4 = 8 THEN T.cuentaactual ELSE substring( T.cuentaactual, 0, $4) END
) AS T;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;


		 """)
		return True