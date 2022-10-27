# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class PeCatalog01(models.Model):
    _name = "pe.catalog.01"
    _inherit = 'pe.abstract.data'
    _description = "Codigo de tipo de documento "

    _order = "code ASC, id ASC"
    

class PeCatalog02(models.Model):
    _name = "pe.catalog.02"
    _inherit = 'pe.abstract.data'
    _description = "Codigo de tipo de monedas"

    _order = "code ASC, id ASC"
    
    country_name = fields.Char("Country Name")
    number_code = fields.Char("Number Code")

class PeCatalog03(models.Model):
    _name = "pe.catalog.03"
    _inherit = 'pe.abstract.data'
    _description = "Código de tipo de unidad de medida comercial"

    _order = "code ASC, id ASC"

class PeCatalog04(models.Model):
    _name = "pe.catalog.04"
    _inherit = 'pe.abstract.data'
    _description = "Código de país"

    _order = "code ASC, id ASC"
    
    code_a2 = fields.Char("Code A2")
    number_code = fields.Char("Number Code")

class PeCatalog05(models.Model):
    _name = "pe.catalog.05"
    _inherit = 'pe.abstract.data'
    _description = "Código de tipos de tributos y otros conceptos"

    _order = "code ASC, id ASC"

    international_code = fields.Char("International Code")
    name_code = fields.Char("Name Code")

class PeCatalog06(models.Model):
    _name = "pe.catalog.06"
    _inherit = 'pe.abstract.data'
    _description = "Código de tipo de documento de identidad"

    _order = "code ASC, id ASC"

class PeCatalog07(models.Model):
    _name = "pe.catalog.07"
    _inherit = 'pe.abstract.data'
    _description = "Código de tipo de afectación del IGV"

    _order = "code ASC, id ASC"

class PeCatalog08(models.Model):
    _name = "pe.catalog.08"
    _inherit = 'pe.abstract.data'
    _description = "Código de tipos de sistema de cálculo del ISC"

    _order = "code ASC, id ASC"

    rate = fields.Float("Rate", digits=(12, 2))

class PeCatalog09(models.Model):
    _name = "pe.catalog.09"
    _inherit = 'pe.abstract.data'
    _description = "Códigos de tipo de nota de crédito electrónica"

    _order = "code ASC, id ASC"

class PeCatalog10(models.Model):
    _name = "pe.catalog.10"
    _inherit = 'pe.abstract.data'
    _description = "Códigos de tipo de nota de débito electrónica"

    _order = "code ASC, id ASC"

class PeCatalog11(models.Model):
    _name = "pe.catalog.11"
    _inherit = 'pe.abstract.data'
    _description = "Códigos de tipo de valor de venta (Resumen diario de boletas y notas)"

    _order = "code ASC, id ASC"

class PeCatalog12(models.Model):
    _name = "pe.catalog.12"
    _inherit = 'pe.abstract.data'
    _description = "Código de documentos relacionados tributarios"

    _order = "code ASC, id ASC"

class PeCatalog14(models.Model):
    _name = "pe.catalog.14"
    _inherit = 'pe.abstract.data'
    _description = "Código de otros conceptos tributarios"

    _order = "code ASC, id ASC"

class PeCatalog15(models.Model):
    _name = "pe.catalog.15"
    _inherit = 'pe.abstract.data'
    _description = "Códigos de elementos adicionales en la factura y boleta electrónica"

    _order = "code ASC, id ASC"

class PeCatalog16(models.Model):
    _name = "pe.catalog.16"
    _inherit = 'pe.abstract.data'
    _description = "Código de tipo de precio de venta unitario"

    _order = "code ASC, id ASC"

class PeCatalog17(models.Model):
    _name = "pe.catalog.17"
    _inherit = 'pe.abstract.data'
    _description = "Código de tipo de operación"

    _order = "code ASC, id ASC"

class PeCatalog18(models.Model):
    _name = "pe.catalog.18"
    _inherit = 'pe.abstract.data'
    _description = "Código de modalidad de transporte"

    _order = "code ASC, id ASC"

class PeCatalog19(models.Model):
    _name = "pe.catalog.19"
    _inherit = 'pe.abstract.data'
    _description = "Código de estado del ítem (resumen diario)"

    _order = "code ASC, id ASC"

class PeCatalog20(models.Model):
    _name = "pe.catalog.20"
    _inherit = 'pe.abstract.data'
    _description = "Código de motivo de traslado"

    _order = "code ASC, id ASC"

class PeCatalog21(models.Model):
    _name = "pe.catalog.21"
    _inherit = 'pe.abstract.data'
    _description = "Código de documentos relacionados (sólo guía de remisión electrónica)"

    _order = "code ASC, id ASC"

class PeCatalog22(models.Model):
    _name = "pe.catalog.22"
    _inherit = 'pe.abstract.data'
    _description = "Código de regimen de percepciones"

    _order = "code ASC, id ASC"

    percent = fields.Float("Percent", digits=(12, 2))

class PeCatalog23(models.Model):
    _name = "pe.catalog.23"
    _inherit = 'pe.abstract.data'
    _description = "Código de regimen de retenciones"

    _order = "code ASC, id ASC"

    percent = fields.Float("Percent", digits=(12, 2))

class PeCatalog24(models.Model):
    _name = "pe.catalog.24"
    _inherit = 'pe.abstract.data'
    _description = "Código de tarifa de servicios públicos"

    _order = "code ASC, id ASC"

class PeCatalog26(models.Model):
    _name = "pe.catalog.26"
    _inherit = 'pe.abstract.data'
    _description = "Tipo de préstamo (créditos hipotecarios)"

    _order = "code ASC, id ASC"

class PeCatalog27(models.Model):
    _name = "pe.catalog.27"
    _inherit = 'pe.abstract.data'
    _description = "Indicador de primera vivienda"

    _order = "code ASC, id ASC"

class PeCatalog51(models.Model):
    _name = "pe.catalog.51"
    _inherit = 'pe.abstract.data'
    _description = "Código de tipo de operación"

    _order = "code ASC, id ASC"

class PeCatalog52(models.Model):
    _name = "pe.catalog.52"
    _inherit = 'pe.abstract.data'
    _description = "Códigos de leyendas"

    _order = "code ASC, id ASC"

class PeCatalog53(models.Model):
    _name = "pe.catalog.53"
    _inherit = 'pe.abstract.data'
    _description = "Códigos de cargos o descuentos"

    _order = "code ASC, id ASC"

class PeCatalog54(models.Model):
    _name = "pe.catalog.54"
    _inherit = 'pe.abstract.data'
    _description = "Códigos de bienes y servicios sujetos a detracciones"

    _order = "code ASC, id ASC"

    rate = fields.Float("Rate", digits=(12, 2))

class PeCatalog55(models.Model):
    _name = "pe.catalog.55"
    _inherit = 'pe.abstract.data'
    _description = "Código de identificación del concepto tributario"

    _order = "code ASC, id ASC"

class PeCatalog56(models.Model):
    _name = "pe.catalog.56"
    _inherit = 'pe.abstract.data'
    _description = "Código de tipo de servicio público"

    _order = "code ASC, id ASC"

class PeCatalog57(models.Model):
    _name = "pe.catalog.57"
    _inherit = 'pe.abstract.data'
    _description = "Código de tipo de servicio públicos - telecomunicaciones"

    _order = "code ASC, id ASC"

class PeCatalog58(models.Model):
    _name = "pe.catalog.58"
    _inherit = 'pe.abstract.data'
    _description = "Código de tipo de medidor (recibo de luz)"

    _order = "code ASC, id ASC"

class PeCatalog59(models.Model):
    _name = "pe.catalog.59"
    _inherit = 'pe.abstract.data'
    _description = "Medios de Pago"

    _order = "code ASC, id ASC"

class PeCatalogReturn(models.Model):
    _name = "pe.catalog.return"
    _inherit = 'pe.abstract.data'
    _description = "Codigos de Retorno"

    _order = "code ASC, id ASC"



class PeCatalogCiiu(models.Model):
    _name = "pe.data.ciiu"
    _inherit = 'pe.abstract.data'
    _description = "ACTIVIDADES ECONOMICAS CON LA CIIU"

    _order = "code ASC, id ASC"


class PeDataDetraction(models.Model):
    _name = "pe.data.detraction"
    _inherit = 'pe.abstract.data'
    _description = "Procentajes de Detracciones"

    _order = "code ASC, id ASC"

    def get_detraction_help(self):
        dtrs = self.search([])
        res = []
        for dtr in dtrs:
            res.append(dtr.code, dtr.description)
        return "\n".join(res)

    def get_detraction_by_code(self, codes):
        res = 0.0
        if type(codes) == list:
            for code in codes:
                if res<float(code):
                    res = float(code)
        else:
            res = int(codes)
        if res == 1.5:
            res = str(res)
        else:
            res = str(int(res))
        return res
        
        
        
