# -*- coding: utf-8 -*-
from itertools import groupby

from odoo import models, fields, api, _


class PeCPESend(models.AbstractModel):
    _inherit = "pe.cpe.send"

    def _get_anticipos(self, invoice_id, cargoDescuentos):
        res = {}
        product_id = self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')
        if product_id:
            taxes = 0.0
            base = 0.0
            exonerated = 0.0
            unaffected = 0.0
            prepaids = []
            inv_line_ids = invoice_id.invoice_line_ids.filtered(
                lambda ln: ln.quantity < 0 and ln.product_id.id == int(product_id))
            for invoice_ids in inv_line_ids.mapped('sale_line_ids').mapped('order_id').mapped('invoice_ids').filtered(lambda inv: inv.pe_invoice_code in ['01', '03'] and inv.id != invoice_id.id and inv.state not in ['draft', 'cancel']):
                # invoice_ids = inv_line.mapped('sale_line_ids').mapped('order_id').mapped('invoice_ids').filtered(lambda inv: inv.pe_invoice_code in ['01','03'] and inv.id != invoice_id.id and inv.state not in ['draft', 'cancel'])
                for inv_id in invoice_ids:
                    vals = {}
                    vals['numero'] = inv_id.name
                    vals['tipoDocumento'] = inv_id.pe_invoice_code
                    vals['monto'] = inv_id.amount_total
                    vals['fecha'] = fields.Date.to_string(
                        invoice_id.pe_invoice_date)
                    taxes += inv_id.amount_untaxed
                    base += invoice_id.amount_untaxed 
                    exonerated += sum(inv_id.invoice_line_ids.filtered(
                        lambda s: s.pe_type_affectation in ['20', '40']).mapped('price_subtotal'))
                    unaffected += sum(inv_id.invoice_line_ids.filtered(
                        lambda s: s.pe_type_affectation in ['30']).mapped('price_subtotal'))
                    prepaids.append(vals)
            if taxes > 0.0:
                val = {}
                val['codigo'] = '04'
                val["monto"] = taxes
                val['base'] = base + taxes
                cargoDescuentos.append(val)
            if exonerated > 0.0:
                val = {}
                val['codigo'] = '05'
                val["monto"] = taxes
                val['base'] = base + exonerated
                cargoDescuentos.append(val)
            if unaffected > 0.0:
                val = {}
                val['codigo'] = '06'
                val["monto"] = taxes
                val['base'] = base + unaffected
                cargoDescuentos.append(val)
            res['cargoDescuentos'] = cargoDescuentos
            res['anticipos'] = prepaids
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    def _prepare_invoice_line(self, **optional_values):
        r = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        invoice_ids = [i.move_id.name for i in self.invoice_lines]
        anticipo =self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')
        if str(anticipo) == str(self.product_id.id):
            r['name'] = "Pago anticipado: {}".format(", ".join(invoice_ids))
        return r