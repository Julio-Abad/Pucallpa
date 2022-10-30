# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class PeTable01(models.Model):
    _name = "pe.table.01"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 1: TIPO DE MEDIO DE PAGO"

    _order = "code ASC, id ASC"

class PeTable02(models.Model):
    _name = "pe.table.02"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 2: TIPO DE DOCUMENTO DE IDENTIDAD"

    _order = "code ASC, id ASC"
    
class PeTable03(models.Model):
    _name = "pe.table.03"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 3: ENTIDAD FINANCIERA"

    _order = "code ASC, id ASC"
    
class PeTable04(models.Model):
    _name = "pe.table.04"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 4: TIPO DE MONEDA"

    _order = "code ASC, id ASC"
    
class PeTable05(models.Model):
    _name = "pe.table.05"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 5: TIPO DE EXISTENCIA"

    _order = "code ASC, id ASC"
    
class PeTable06(models.Model):
    _name = "pe.table.06"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 6: CÓDIGO DE LA UNIDAD DE MEDIDA"

    _order = "code ASC, id ASC"
    
class PeTable10(models.Model):
    _name = "pe.table.10"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 10: TIPO DE COMPROBANTE DE PAGO O DOCUMENTO"

    _order = "code ASC, id ASC"
    
class PeTable11(models.Model):
    _name = "pe.table.11"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 11: CÓDIGO DE LA ADUANA"

    _order = "code ASC, id ASC"
    
class PeTable12(models.Model):
    _name = "pe.table.12"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 12: TIPO DE OPERACIÓN"

    _order = "code ASC, id ASC"
    
class PeTable13(models.Model):
    _name = "pe.table.13"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 13: CATÁLOGO DE EXISTENCIAS"

    _order = "code ASC, id ASC"
    
class PeTable14(models.Model):
    _name = "pe.table.14"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 14: MÉTODO DE VALUACIÓN"

    _order = "code ASC, id ASC"
    
class PeTable15(models.Model):
    _name = "pe.table.15"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 15: TIPO DE TÍTULO"

    _order = "code ASC, id ASC"
    
class PeTable16(models.Model):
    _name = "pe.table.16"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 16: TIPO DE ACCIONES O PARTICIPACIONES"

    _order = "code ASC, id ASC"
    
class PeTable17(models.Model):
    _name = "pe.table.17"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 17: PLAN DE CUENTAS"

    _order = "code ASC, id ASC"
    
class PeTable18(models.Model):
    _name = "pe.table.18"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 18: TIPO DE ACTIVO FIJO"

    _order = "code ASC, id ASC"
    
class PeTable19(models.Model):
    _name = "pe.table.19"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 19: ESTADO DEL ACTIVO FIJO"

    _order = "code ASC, id ASC"
    
class PeTable20(models.Model):
    _name = "pe.table.20"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 20: MÉTODO DE DEPRECIACIÓN"

    _order = "code ASC, id ASC"
    
class PeTable21(models.Model):
    _name = "pe.table.21"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 21: CÓDIGO DE AGRUPAMIENTO DEL COSTO DE PRODUCCIÓN VALORIZADO ANUAL"

    _order = "code ASC, id ASC"
    
class PeTable22(models.Model):
    _name = "pe.table.22"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 22: CATÁLOGO DE ESTADOS FINANCIEROS"

    _order = "code ASC, id ASC"
    
class PeTable25(models.Model):
    _name = "pe.table.25"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 25 'CONVENIOS PARA EVITAR LA DOBLE TRIBUTACIÓN'"

    _order = "code ASC, id ASC"
    
class PeTable27(models.Model):
    _name = "pe.table.27"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 27: TIPO DE VINCULACION ECONOMICA"

    _order = "code ASC, id ASC"
    
class PeTable28(models.Model):
    _name = "pe.table.28"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 28: PATRIMONIO NETO"

    _order = "code ASC, id ASC"
    
class PeTable30(models.Model):
    _name = "pe.table.30"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 30: CLASIFICACIÓN DE LOS BIENES Y SERVICIOS ADQUIRIDOS"

    _order = "code ASC, id ASC"
    
class PeTable31(models.Model):
    _name = "pe.table.31"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 31: TIPO DE RENTA"

    rent_code = fields.Char("Rent Code")
    
    _order = "code ASC, id ASC"
    
class PeTable32(models.Model):
    _name = "pe.table.32"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 32: MODALIDAD DEL SERVICIO PRESTADO POR EL SUJETO NO DOMICILIADO"

    _order = "code ASC, id ASC"
    
class PeTable33(models.Model):
    _name = "pe.table.33"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 33: EXONERACIONES DE OPERACIONES DE NO DOMICILIADOS (ART. 19 DE LA LEY DEL IMPUESTO A LA RENTA)"

    _order = "code ASC, id ASC"
    
class PeTable34(models.Model):
    _name = "pe.table.34"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 34: CÓDIGO DE LOS RUBROS DE LOS ESTADOS FINANCIEROS"

    _order = "code ASC, id ASC"
    
class PeTable35(models.Model):
    _name = "pe.table.35"
    _inherit = 'pe.abstract.data'
    _description = "TABLA 35: PAISES"

    _order = "code ASC, id ASC"
