from librecpe import Documento
from odoo import fields, models
from base64 import decodestring
import json

class PeCPESend(models.AbstractModel):
    
    _name = "pe.cpe.send"
    _description = "Send Document"
    
    def _empresa(self, partner_id):
        vals = {}
        branch_id = partner_id
        partner_id = partner_id.parent_id or partner_id
        vals['nombre'] = partner_id.pe_legal_name and partner_id.pe_legal_name!='-' and partner_id.pe_legal_name or partner_id.name
        vals['nomComercial'] = partner_id.pe_commercial_name and partner_id.pe_commercial_name!='-' and partner_id.pe_commercial_name or ""
        vals['tipoDocumento'] = partner_id.pe_doc_type or '-'
        vals['numDocumento'] = partner_id.vat or '-'
        vals['direccion'] = branch_id.street or ''
        vals['urbanizacion'] = branch_id.street2 or ''
        vals['ubigeo'] = branch_id.l10n_pe_district.code or ''
        vals['distrito'] = branch_id.l10n_pe_district.name or ''
        vals['provincia'] = branch_id.city_id.name or ''
        vals['region'] = branch_id.state_id.name or ''
        vals['codPais'] = branch_id.country_id.code or ''
        vals['email'] = branch_id.email or ''
        return vals
    
    def _get_adquirente(self, partner_id):
        return {'adquirente': self._empresa(partner_id)} 
    
    def _get_emisor(self, company_id, cpe_id = False, branch_code = False, user_id = False):
        partner_id = company_id.partner_id
        vals = self._empresa(partner_id)
        vals.update({'codEstablecimiento': branch_code or company_id.pe_branch_code})
        return {'emisor':vals}
    
    def _get_descuento_global(self, invoice_id, invoice_line_ids):
        discount = 0.0
        res = {}
        product_id = self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')
        product_id = product_id and int(product_id) or False
        for line in invoice_line_ids.filtered(lambda ln: ln.price_subtotal <0):
            if line.product_id.id ==product_id:
                continue
            discount += line._get_price_total_and_subtotal().get('price_subtotal')
        cargoDescuentos = []
        if abs(discount)> 0.0:  
            val = {}
            val["monto"] = abs(discount)
            val['base'] = invoice_id.amount_untaxed + abs(discount)
            cargoDescuentos.append(val)
        res['cargoDescuentos'] = cargoDescuentos
        return res
    
    def _get_motivo(self, invoice_id):
        vals = {}
        vals['motivo'] = invoice_id.ref
        if invoice_id.pe_invoice_code in ['07']:
            vals['codigoNota'] = invoice_id.pe_credit_note_code
        elif invoice_id.pe_invoice_code in ['08']:
            vals['codigoNota'] = invoice_id.pe_debit_note_code
        return vals
    
    def _get_documentos_modificados(self, invoice_id):
        res = []
        if invoice_id.pe_invoice_code in ['07']:
            vals = {'numero': invoice_id.reversed_entry_id.name, 
                    'tipoDocumento': invoice_id.reversed_entry_id.pe_invoice_code}
            res.append(vals)
        elif invoice_id.pe_invoice_code in ['08']:
            vals = {'numero': invoice_id.debit_origin_id.name, 
                    'tipoDocumento': invoice_id.debit_origin_id.pe_invoice_code}
            res.append(vals)
        return {'documentosModificados': res}
    
    def _get_anticipos(self, invoice_id, cargoDescuentos):
        res={}
        product_id = self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')
        if product_id:
            taxes = 0.0
            exonerated = 0.0
            unaffected = 0.0
            prepaids = []
            for inv_line in invoice_id.invoice_line_ids.filtered(lambda ln: ln.quantity <0 and ln.product_id.id==int(product_id)):
                invoice_ids = inv_line.mapped('sale_line_ids').mapped('invoice_lines').mapped('move_id').filtered(lambda inv: inv.pe_invoice_code in ['01','03'] and inv.id != invoice_id.id and inv.state not in ['draft', 'cancel'])
                move_names = []
                for inv_id in invoice_ids:
                    if inv_id == invoice_id:
                        continue
                    if inv_id.name in move_names:
                        continue
                    move_names.append(inv_id.name)
                    vals = {}
                    vals['numero'] = inv_id.name
                    vals['tipoDocumento'] = inv_id.pe_invoice_code
                    vals['monto'] = inv_id.amount_total
                    vals['impuestos'] = inv_id.amount_tax
                    vals['fecha'] = fields.Date.to_string(invoice_id.pe_invoice_date)
                    #vals.update(self._get_tributos(inv_id))
                    taxes = inv_id.amount_untaxed
                    exonerated += sum(inv_id.invoice_line_ids.filtered(lambda s:s.pe_type_affectation in ['20', '40']).mapped('price_subtotal'))
                    unaffected += sum(inv_id.invoice_line_ids.filtered(lambda s:s.pe_type_affectation in ['30']).mapped('price_subtotal'))
                    prepaids.append(vals)
            if taxes> 0.0:  
                val = {}
                val['codigo'] = '04'
                val["monto"] = taxes
                val['base'] = invoice_id.amount_untaxed + taxes
                cargoDescuentos.append(val)
            if exonerated> 0.0:  
                val = {}
                val['codigo'] = '05'
                val["monto"] = taxes
                val['base'] = invoice_id.amount_untaxed + exonerated
                cargoDescuentos.append(val)
            if unaffected> 0.0:  
                val = {}
                val['codigo'] = '06'
                val["monto"] = taxes
                val['base'] = invoice_id.amount_untaxed + unaffected
                cargoDescuentos.append(val)
            res['cargoDescuentos'] = cargoDescuentos
            res['anticipos'] = prepaids
        return res
        
    def _get_detalles(self, invoice_line_ids):
        res = []
        for line in invoice_line_ids:
            if line.display_type and line.display_type == 'line_section':
                continue
            vals = {}
            vals['codUnidadMedida'] = line.product_uom_id.pe_unit_code or "NIU"
            vals['cantidad'] = line.quantity
            values = {
                    'price_unit':line.price_unit, 
                    'quantity': line.quantity, 
                    'discount': line.discount,
                    'currency':line.currency_id,
                    'product':line.product_id,
                    'partner':line.partner_id,
                    'taxes':line.tax_ids,
                    'move_type':line.move_id.move_type,
                    }
            values.update({'quantity':1.0})
            totals = line._get_price_total_and_subtotal_model(**values)
            if line.discount == 100:
                values.update({'discount':0.0, 'quantity':line.quantity})
                vals['mtoValorVentaItem'] = line._get_price_total_and_subtotal_model(**values).get('price_subtotal')
            else:
                vals['mtoValorVentaItem'] = line.price_subtotal #totals.get('price_subtotal')
            if line.move_id.pe_invoice_code in ['07','08']:
                values.update({'quantity':line.quantity, 'discount':line.discount, 'taxes':line.tax_ids.with_context(round=False)})
            else:
                values.update({'quantity':line.quantity, 'discount':line.discount, 'taxes':line.tax_ids.with_context(round=False)})
            vals['mtoPrecioVentaUnitario'] = line._get_price_total_and_subtotal_model(**values).get('price_total')/line.quantity
            
            if totals.get('price_total')==0.0 and line.discount==100:
                values.update({'quantity':line.quantity, 'discount':0.0, 'taxes':line.tax_ids.with_context(round=False)})
                vals['mtoValorReferencialUnitario'] = line.with_context(round=False)._get_price_total_and_subtotal_model(**values).get('price_subtotal')/line.quantity
            vals['tipAfectacion'] = line.pe_type_affectation
            values.update({'taxes':line.tax_ids})
            cargoDescuentos = []
            sumTotTributosItem = 0.0
            if line.pe_type_affectation in ['10','20','30', '40']:
                taxes = line._get_pe_all_taxes()
            else:
                taxes = line._get_pe_all_taxes(taxes=line.tax_ids.filtered(lambda tax: tax.pe_tax_type.code not in['9996']), discount = 0.0)
            tributos = []
            
            if line.discount > 0.0 and not line.discount == 100:
                values.update({'quantity': line.quantity, 'discount': 0.0})
                all_amount = line._get_price_total_and_subtotal_model(**values)
                values.update({'discount':line.discount})
                disc_amount = line._get_price_total_and_subtotal_model(**values)
                val = {}
                val["monto"] = all_amount.get('price_subtotal') - disc_amount.get('price_subtotal')
                val['base'] = all_amount.get('price_subtotal')
                cargoDescuentos.append(val)
            icbper_amount = 0.0
            for tax in taxes.get('taxes', []):
                tax_id = line.env['account.tax'].browse([tax.get('id')])
                percent = 0.0
                if line.pe_type_affectation not in ['10','20','30', '40']:
                    percent = tax_id.amount
                    tax_id = line.tax_ids.filtered(lambda tax: tax.pe_tax_type.code in ['9996'])
                if not tax_id.pe_is_charge:
                    # if tax_id.pe_tax_type.code != '7152':
                    if tax_id.pe_tax_type.code == '7152':
                        #vals['mtoPrecioVentaUnitario'] = tax.get('base', 0.0)/(line.quantity or 1)
                        icbper_amount += tax.get('amount', 0.0)
                    sumTotTributosItem+= tax.get('amount')
                    val = {
                        'ideTributo':tax_id.pe_tax_type.code,
                        'nomTributo':tax_id.pe_tax_type.name_code,
                        'codTipTributo':tax_id.pe_tax_type.international_code,
                        'montoTributo':tax.get('amount', 0.0),
                        'baseTributo':tax.get('base', 0.0),
                        'procentaje':percent or tax_id.amount,
                        }
                    #if tax_id.pe_tax_type.code == '7152':
                    #    val['cantidad'] = int(line.quantity)
                    tributos.append(val)
                elif tax_id.pe_is_charge:
                    val = {}
                    val['tipo'] = 'cargo'
                    val["monto"] = tax.get('amount', 0.0)
                    val['base'] = tax.get('base', 0.0)
                    cargoDescuentos.append(val)
            if icbper_amount>0.0:
                vals['mtoPrecioVentaUnitario'] = (taxes.get('total_included') - icbper_amount)/(line.quantity or 1)
            vals['sumTotTributosItem'] = sumTotTributosItem
            
            vals['cargoDescuentos'] = cargoDescuentos
            vals['tributos'] = tributos
            vals['descripcion'] = line.name
            vals['codProducto'] = line.product_id.default_code or ''
            vals['codProductoSUNAT'] = line.product_id.pe_unspsc_code or line.product_id.categ_id.pe_unspsc_code or ''
            vals['placa'] = line.pe_license_plate
            if line.pe_type_affectation in ['10','20','30'] and line.move_id.pe_invoice_code not in ['07','08']:
                values.update({'quantity':line.quantity, 'discount':0.0, 'taxes':line.tax_ids.with_context(round=False)})
            else:
                values.update({'quantity':line.quantity, 'discount': line.discount, 'taxes':line.tax_ids.with_context(round=False)})
            vals['mtoValorUnitario'] = abs(line.with_context(round=False)._get_price_total_and_subtotal_model(**values).get('price_subtotal'))/line.quantity
            res.append(vals)
        return {'detalles': res}
    
    def _get_operaciones(self, invoice_line_ids):
        taxes = 0.0
        exonerated = 0.0
        unaffected = 0.0
        exports = 0.0
        free = 0.0
        res = []
        for line in invoice_line_ids.filtered(lambda ln: ln.quantity>0.0):
            if line.pe_type_affectation in ['10']:
                taxes+=line._get_pe_all_taxes().get('total_excluded', 0.0)
            elif line.pe_type_affectation in ['20']:
                exonerated+=line._get_pe_all_taxes().get('total_excluded', 0.0)
            elif line.pe_type_affectation in ['30']:
                unaffected+=line._get_pe_all_taxes().get('total_excluded', 0.0)
            elif line.pe_type_affectation in ['40']:
                exports+=line._get_pe_all_taxes().get('total_excluded', 0.0)
            elif line.pe_type_affectation not in ['10', '20', '30', '40']:
                free+=line._get_pe_all_taxes(discount=0.0).get('total_excluded', 0.0)
        if taxes> 0.0:
            res.append({'codigo': "01", "total":taxes})
        if exonerated> 0.0:
            res.append({'codigo': "02", "total":exonerated})
        if unaffected> 0.0:
            res.append({'codigo': "03", "total":unaffected})
        if exports> 0.0:
            res.append({'codigo': "04", "total":exports})
        if free> 0.0:
            res.append({'codigo': "05", "total":free})
        return {"operaciones": res}
    
    def _get_leyenda(self, invoice_id):
        res = []
        for legend in invoice_id.pe_legend_ids:
            vals = {}
            vals['codLeyenda'] = legend.code
            vals['desLeyenda'] = legend.name
            res.append(vals)
        return {'leyendas': res}
    
    def _get_tributos(self, invoice_id, summary = False):
        taxes = invoice_id._compute_invoice_taxes_by_sunat_code()
        tributos = []
        icbper_amount = 0.0
        if summary and not invoice_id.line_ids.filtered(lambda line: line.tax_line_id and line.tax_line_id.pe_tax_type.code == '1000'):
            tax_id = self.env['account.tax'].search([('type_tax_use','=','sale'),('pe_tax_type.code','=','1000')],limit=1)
            val = {
                'ideTributo':tax_id.pe_tax_type.code,
                'nomTributo':tax_id.pe_tax_type.name_code,
                'codTipTributo':tax_id.pe_tax_type.international_code,
                'montoTributo':0.0,
                'baseTributo':0.0,
                'procentaje':tax_id.amount,
                }
            if tax_id.pe_tax_type.code == '7152':
                icbper_amount+= tax_id.get('amount', 0.0)
            tributos.append(val)
        for code, tax in taxes:
            tax_id = invoice_id.env['account.tax'].browse([tax.get('tax_id')])
            val = {
                'ideTributo':tax_id.pe_tax_type.code,
                'nomTributo':tax_id.pe_tax_type.name_code,
                'codTipTributo':tax_id.pe_tax_type.international_code,
                'montoTributo':tax.get('amount', 0.0),
                'baseTributo':tax.get('base', 0.0),
                'procentaje':tax_id.amount,
                }
            if tax_id.pe_tax_type.code == '7152':
                icbper_amount+= tax.get('amount', 0.0)
            tributos.append(val)
        totalTributos = invoice_id.amount_tax
        return {'tributos': tributos, 'totalTributos':totalTributos}

    def _get_detraccion(self, invoice_id):
        vals = {}
        if invoice_id.pe_subject_detraction and invoice_id.pe_detraction_amount>0.0:
            vals['codigo'] = invoice_id.pe_subject_detraction
            vals['cuentaBanco'] = invoice_id.company_id.pe_detraction_account_number
            vals['monto'] = invoice_id.pe_detraction_amount
            vals['porcentaje'] =  invoice_id.pe_detraction_percentage * 100
        return {'detraccion': vals}

    def _get_retencion(self, invoice_id):
        vals = {}
        if invoice_id.pe_subject_retention and invoice_id.pe_retention_amount>0.0:
            vals['codigo'] = invoice_id.pe_subject_retention
            vals['monto'] = invoice_id.pe_retention_amount
            vals['base'] = invoice_id.amount_total
            vals['porcentaje'] =  invoice_id.pe_retention_percentage * 100
        return {'retencion': vals}


    def _get_medio_pago(self, invoice_id):
        vals = {}
        vals['tipo'] = invoice_id.pe_payment_lines and 'Credito' or 'Contado'
        cuotas = []
        for line in invoice_id.pe_payment_lines:
            cuotas.append({'monto': line.amount, 'fecha': fields.Date.to_string(line.date) })
        vals['cuotas'] = cuotas
        return {'medioPago': vals}
    
    def _get_document_values(self, invoice_id):
        documento = Documento()
        vals = {}
        anticipos = 0.0
        anticipos_untaxed = 0.0
        product_id = self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')
        if product_id:
            if invoice_id.invoice_line_ids.filtered(lambda ln: ln.quantity <0 and ln.product_id.id==int(product_id)):
                anticipos = abs(sum(invoice_id.invoice_line_ids.filtered(lambda ln: ln.quantity <0 and ln.product_id.id==int(product_id)).mapped('price_total')))
                anticipos_untaxed = abs(sum(invoice_id.invoice_line_ids.filtered(lambda ln: ln.quantity <0 and ln.product_id.id==int(product_id)).mapped('price_subtotal')))
        vals['numero'] = invoice_id.name
        vals['fecEmision'] = fields.Datetime.to_string(invoice_id.pe_invoice_date)
        if invoice_id.invoice_date_due > invoice_id.pe_invoice_date.date():
            vals['fecVencimiento'] = fields.Date.to_string(invoice_id.invoice_date_due) 
        vals['tipoDocumento'] = invoice_id.pe_invoice_code
        vals['tipOperacion'] = invoice_id.pe_operation_type
        vals['tipMoneda'] = invoice_id.currency_id.pe_currency_code or invoice_id.currency_id.name
        vals['referencia'] = invoice_id.ref or invoice_id.invoice_origin or ''
        vals['totalValVenta'] = invoice_id.amount_untaxed + anticipos_untaxed
        vals['totalImpVenta'] = invoice_id.amount_total + anticipos
        vals['totalDescuentos'] = 0.0
        vals['totalCargos'] = 0.0
        vals['totalAnticipos'] = anticipos
        vals['totalVenta'] = invoice_id.amount_total
        vals['notas'] = invoice_id.narration or ''
        if invoice_id.currency_id != self.env.ref('base.PEN'):
            vals['tipoDeCambio'] = invoice_id.currency_id.with_context(date=fields.Date.to_string(invoice_id.pe_invoice_date), 
                                                                       company_id= invoice_id.company_id.id).compute(1, self.env.ref('base.PEN'))
            
        if invoice_id.pe_invoice_code in ['07', '08']:
            vals.update(self._get_motivo(invoice_id))
            vals.update(self._get_documentos_modificados(invoice_id))
        if invoice_id.pe_invoice_code not in ['07', '08']:
            vals.update(self._get_detraccion(invoice_id))
            vals.update(self._get_retencion(invoice_id))
        vals.update(self._get_medio_pago(invoice_id))
        vals.update(self._get_adquirente(invoice_id.partner_id))
        vals.update(self._get_emisor(invoice_id.company_id, invoice_id, False, invoice_id.invoice_user_id))
        vals.update(self._get_leyenda(invoice_id))
        vals.update(self._get_detalles(invoice_id.invoice_line_ids.filtered(lambda ln: ln.price_subtotal >= 0.0)))
        vals.update(self._get_descuento_global(invoice_id, invoice_id.invoice_line_ids))
        if product_id:
            if invoice_id.invoice_line_ids.filtered(lambda ln: ln.quantity <0 and ln.product_id.id==int(product_id)):
                vals.update(self._get_anticipos(invoice_id, vals.get('cargoDescuentos', [])))
        vals.update(self._get_tributos(invoice_id))
        return vals
    
    def _get_document(self, invoice_id, key, crt, xml=None):
        vals = {}
        documento = Documento()
        if not xml:
            #invoice_id = self.document.invoice_ids[0]
            vals = self._get_document_values(invoice_id)
            documento.setDocument(vals)
        data= documento.getDocumento(key, crt, xml)
        # res = json.loads(data)
        return data
    
    def _get_documentos(self, invoice_ids):
        documentos = []
        inv_ids = self.env['account.move'].search([('id','in',invoice_ids.ids)], order="pe_invoice_code ASC, name ASC")
        for invoice_id in inv_ids:
            vals = {}
            vals['numero'] = invoice_id.name
            vals['fecEmision'] = fields.Datetime.to_string(invoice_id.pe_invoice_date) 
            vals['fecVencimiento'] = fields.Date.to_string(invoice_id.invoice_date_due) 
            vals['tipoDocumento'] = invoice_id.pe_invoice_code
            vals['tipOperacion'] = invoice_id.pe_operation_type
            vals['tipMoneda'] = invoice_id.currency_id.pe_currency_code or invoice_id.currency_id.name
            vals['condicion'] = invoice_id.pe_condition_code
            vals['totalValVenta'] = invoice_id.amount_untaxed
            vals['totalImpVenta'] = invoice_id.amount_total
            vals['totalDescuentos'] = 0.0
            vals['totalCargos'] = 0.0
            vals['totalAnticipos'] = 0.0
            vals['totalVenta'] = invoice_id.amount_total
            
            vals['totalTributos'] = invoice_id.amount_tax
            
            if invoice_id.pe_invoice_code in ['07', '08']:
                vals.update(self._get_motivo(invoice_id))
                vals.update(self._get_documentos_modificados(invoice_id))
            vals.update(self._get_adquirente(invoice_id.partner_id))
            vals.update(self._get_operaciones(invoice_id.invoice_line_ids))
            #vals.update(self._get_descuento_global(invoice_id, invoice_id.invoice_line_ids))
            vals.update(self._get_tributos(invoice_id, summary=True))
            documentos.append(vals)
        return {'documentos': documentos}
            
    
    def _get_resumen_diario(self, cpe_id, key, crt):
        vals = {}
        vals['numero'] = cpe_id.name
        vals['tipoDocumento'] = 'rc'
        vals['fecEnvio'] = fields.Datetime.to_string(cpe_id.pe_send_date) 
        vals['fecEmision'] = fields.Datetime.to_string(cpe_id.pe_date) 
        vals.update(self._get_emisor(cpe_id.company_id, cpe_id, branch_code=cpe_id.pe_branch_code))
        vals.update(self._get_documentos(cpe_id.summary_ids))
        documento = Documento(tipo = 'rc')
        documento.setDocument(vals)
        data= documento.getDocumento(key, crt)
        return data
    
    def _get_documentos_anulados(self, cpe_id, key, crt):
        vals = {}
        vals['numero'] = cpe_id.name
        vals['tipoDocumento'] = 'ra'
        vals['fecEnvio'] = fields.Datetime.to_string(cpe_id.pe_send_date) 
        vals['fecEmision'] = fields.Datetime.to_string(cpe_id.pe_date) 
        vals.update(self._get_emisor(cpe_id.company_id, cpe_id, branch_code=cpe_id.pe_branch_code))
        documentosAnulados = []
        for invoice_id in cpe_id.voided_ids:
            val = {}
            val['tipoDocumento'] = invoice_id.pe_invoice_code
            val['numero'] = invoice_id.name
            val['descripcion'] = "Anulado"
            documentosAnulados.append(val)
        vals.update({'documentosAnulados':documentosAnulados})
        documento = Documento(tipo = 'ra')
        documento.setDocument(vals)
        data= documento.getDocumento(key, crt)
        return data
    
    def get_type(self, cpe_id):
        res = False
        if cpe_id.type in ['sync']:
            if cpe_id.invoice_ids:
                res = cpe_id.invoice_ids[0].pe_invoice_code
        else:
            res = cpe_id.type
        return res
    
    def send_document(self, cpe_id, type='sync', xml = None):
        soap = self.get_webservice(cpe_id)
        
        vals = {}
        if cpe_id.company_id.pe_ws_server in ['nubefact_pse']:
            if cpe_id._name == 'pe.cpe.ra':
                vals['numero'] = cpe_id.name
                vals['tipoDocumento'] = 'ra'
                vals['fecEnvio'] = fields.Datetime.to_string(cpe_id.pe_send_date) 
                vals['fecEmision'] = fields.Datetime.to_string(cpe_id.pe_date) 
                vals.update(self._get_emisor(cpe_id.company_id, cpe_id, branch_code=cpe_id.pe_branch_code))
                documentosAnulados = []
                for invoice_id in cpe_id.voided_ids:
                    val = {}
                    val['tipoDocumento'] = invoice_id.pe_invoice_code
                    val['numero'] = invoice_id.name
                    val['descripcion'] = "Anulado"
                    documentosAnulados.append(val)
                vals.update({'documentosAnulados':documentosAnulados})
                documento = Documento(tipo = 'ra')
                documento.setDocument(vals)
            else:
                documento = Documento()
                data = self._get_document_values(cpe_id)
                documento.setDocument(data)
            res = documento.enviarDocumento(soap, tipo = type)
            vals.update(res)
        else:
            nombre_documento = cpe_id._pe_cpe_document_name()
            xml = xml or cpe_id.attachment_id.datas
            if not xml:
                val = self.get_document(cpe_id)
                vals.update(val)
                xml = vals.get('xml_firmado')
            tipo = type
            documento = Documento()
            data = documento.enviarDocumento(soap, nombre_documento, tipo, xml)
            vals.update(data)
        return vals
    
    def get_webservice(self, cpe_id):
        soap = {}
        soap['ruc'] = cpe_id.company_id.vat
        soap['usuario'] = cpe_id.company_id.pe_ws_user
        soap['clave'] = cpe_id.company_id.pe_ws_password
        soap['servidor'] =  cpe_id.company_id.pe_ws_server
        soap['url'] = cpe_id.company_id.pe_ws_url
        if cpe_id._name not in ["pe.cpe.ra", "pe.cpe.rc"] and self.env.context.get('document_status'):
            soap['url'] = cpe_id.company_id.pe_ws_status_url or cpe_id.company_id.pe_ws_url
        if cpe_id._name in ["pe.eguide"]:
            soap['url'] = cpe_id.company_id.pe_guide_ws_url
        return soap
    
    def get_document_status(self, cpe_id, tipo):
        documento = Documento()
        soap = self.get_webservice(cpe_id)
        if cpe_id.company_id.pe_ws_server in ['nubefact_pse']:
            if cpe_id._name == 'account.edi.document':
                nombre_documento = cpe_id._pe_cpe_document_name(cpe_id.move_id)
            elif cpe_id._name == 'pe.eguide':
                nombre_documento = cpe_id._pe_cpe_document_name(cpe_id.picking_id)
            else:
                nombre_documento = cpe_id._pe_cpe_document_name(cpe_id.voided_ids[0])
        else:
            nombre_documento = cpe_id._pe_cpe_document_name()
        ticket = cpe_id.pe_ticket
        data = documento.obtenerEstadoDocumento(soap, nombre_documento, tipo, ticket)
        return data
    
    def get_document(self, cpe_id):
        data = {}
        key = cpe_id.company_id.pe_private_key
        crt = cpe_id.company_id.pe_public_key
        if cpe_id._name=="account.move":
            data = self._get_document(cpe_id, key, crt, None)
        elif cpe_id._name=="pe.cpe.rc":
            data = self._get_resumen_diario(cpe_id, key, crt)
        elif cpe_id._name=="pe.cpe.ra":
            data = self._get_documentos_anulados(cpe_id, key, crt)
        return data
    
