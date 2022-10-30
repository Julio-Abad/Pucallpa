from librecpe import Documento
from odoo import fields, models
from base64 import decodestring
import json

class PeCPESend(models.AbstractModel):
    
    _inherit = "pe.cpe.send"
    
    def _get_detalles_guia(self, line_ids):
        res = []
        for line_id in line_ids:
            vals = {}
            if line_id.quantity_done >0:
                vals['cantidad'] = line_id.quantity_done
            else:
                vals['cantidad'] = line_id.product_uom_qty
            if line_id._name == 'stock.move':
                vals['codUnidadMedida'] = line_id.product_uom.pe_unit_code or 'NIU'
            else:
                vals['codUnidadMedida'] = line_id.product_uom_id.pe_unit_code or 'NIU'
            vals['descripcion'] = line_id.product_id.name
            vals['codProducto'] = line_id.product_id.default_code or ''
            res.append(vals)
        return res
    
    def _get_eguide_document(self, picking_id, key, crt):
        vals = {}
        vals['numero'] = picking_id.pe_guide_number
        vals['tipoDocumento'] = '09'
        vals['observacion'] = picking_id.note or ''
        vals['fecEmision'] = picking_id.pe_date_issue and fields.Date.to_string(picking_id.pe_date_issue) or ''
        vals.update(self._get_emisor(picking_id.company_id))
        if picking_id.pe_related_number and picking_id.pe_related_code :
            relacionado = {'numero': picking_id.pe_related_number,
                           'tipoDocumento': picking_id.pe_related_code }
            vals['documentosRelacionados'] = [relacionado]
        
        if picking_id.picking_type_id.code == 'outgoing':
            sender_id = picking_id.partner_id.parent_id or picking_id.partner_id
        else:
            sender_id = picking_id.picking_type_id.warehouse_id.partner_id
        
        vals['remitente'] = self._empresa(sender_id)
        if picking_id.picking_type_id.code == 'outgoing':
            partner_id = picking_id.partner_id.parent_id or picking_id.partner_id
        else:
            partner_id = picking_id.picking_type_id.warehouse_id.partner_id
        vals['destinatario'] = self._empresa(partner_id)
        if picking_id.pe_supplier_id:
            vals['establecimientoTercero'] = self._empresa(picking_id.pe_supplier_id)
        vals['motivo'] = picking_id.pe_transfer_code
        vals['descripcion'] = picking_id.origin or ''
        vals['transbordo'] = picking_id.pe_is_programmed and 'true' or 'false'
        vals['pesoBruto'] = picking_id.pe_gross_weight
        vals['bultos'] = picking_id.pe_unit_quantity
        vals['modoTraslado'] = picking_id.pe_transport_mode 
        vals['fechaTraslado'] =  (picking_id.date_done or picking_id.scheduled_date).strftime("%Y-%m-%d")
        transportistas = []
        for pe_carrier_id in picking_id.pe_carrier_ids:
            transportistas.append(self._empresa(pe_carrier_id))
        vals['transportistas'] = transportistas
        placa = picking_id.pe_fleet_ids.filtered(lambda s: s.is_main == True).name or (picking_id.pe_fleet_ids and picking_id.pe_fleet_ids[0].name) or ''
        vals['placa'] = placa
        if picking_id.picking_type_id.code == 'outgoing':
            partner_id = picking_id.partner_id
        else:
            partner_id = picking_id.picking_type_id.warehouse_id.partner_id
        vals['ubigeoLlegada'] = partner_id.l10n_pe_district.code 
        vals['direccionLlegada'] = partner_id.street
        
        vehículos = []
        for pe_fleet_id in picking_id.pe_fleet_ids:
            vehículos.append({'principal': pe_fleet_id.is_main, 'placa':pe_fleet_id.name})
        if picking_id.picking_type_id.code == 'outgoing':
            sender_id = picking_id.picking_type_id.warehouse_id.partner_id
        else:
            sender_id = picking_id.partner_id
        vals['ubigeoPartida'] = sender_id.l10n_pe_district.code 
        vals['direccionPartida'] = sender_id.street
        vals['detalles'] = self._get_detalles_guia(picking_id.move_ids_without_package or picking_id.move_line_ids_without_package)
        documento = Documento()
        documento.setDocument(vals)
        data= documento.getDocumento(key, crt)
        return data
    
    def _get_eguide_document2(self, picking_id):
        vals = {}
        vals['numero'] = picking_id.pe_guide_number
        vals['tipoDocumento'] = '09'
        vals['observacion'] = picking_id.note or ''
        vals['fecEmision'] = picking_id.pe_date_issue and fields.Date.to_string(picking_id.pe_date_issue) or ''
        vals.update(self._get_emisor(picking_id.company_id))
        if picking_id.pe_related_number and picking_id.pe_related_code :
            relacionado = {'numero': picking_id.pe_related_number,
                           'tipoDocumento': picking_id.pe_related_code }
            vals['documentosRelacionados'] = [relacionado]
        
        if picking_id.picking_type_id.code == 'outgoing':
            sender_id = picking_id.partner_id.parent_id or picking_id.partner_id
        else:
            sender_id = picking_id.picking_type_id.warehouse_id.partner_id
        
        vals['remitente'] = self._empresa(sender_id)
        if picking_id.picking_type_id.code == 'outgoing':
            partner_id = picking_id.partner_id.parent_id or picking_id.partner_id
        else:
            partner_id = picking_id.picking_type_id.warehouse_id.partner_id
        vals['destinatario'] = self._empresa(partner_id)
        if picking_id.pe_supplier_id:
            vals['establecimientoTercero'] = self._empresa(picking_id.pe_supplier_id)
        vals['motivo'] = picking_id.pe_transfer_code
        vals['descripcion'] = picking_id.origin or ''
        vals['transbordo'] = picking_id.pe_is_programmed and 'true' or 'false'
        vals['pesoBruto'] = picking_id.pe_gross_weight
        vals['bultos'] = picking_id.pe_unit_quantity
        vals['modoTraslado'] = picking_id.pe_transport_mode 
        vals['fechaTraslado'] =  (picking_id.date_done or picking_id.scheduled_date).strftime("%Y-%m-%d")
        transportistas = []
        for pe_carrier_id in picking_id.pe_carrier_ids:
            transportistas.append(self._empresa(pe_carrier_id))
        vals['transportistas'] = transportistas
        placa = picking_id.pe_fleet_ids.filtered(lambda s: s.is_main == True).name or (picking_id.pe_fleet_ids and picking_id.pe_fleet_ids[0].name) or ''
        vals['placa'] = placa
        if picking_id.picking_type_id.code == 'outgoing':
            partner_id = picking_id.partner_id
        else:
            partner_id = picking_id.picking_type_id.warehouse_id.partner_id
        vals['ubigeoLlegada'] = partner_id.l10n_pe_district.code 
        vals['direccionLlegada'] = partner_id.street
        
        vehículos = []
        for pe_fleet_id in picking_id.pe_fleet_ids:
            vehículos.append({'principal': pe_fleet_id.is_main, 'placa':pe_fleet_id.name})
        if picking_id.picking_type_id.code == 'outgoing':
            sender_id = picking_id.picking_type_id.warehouse_id.partner_id
        else:
            sender_id = picking_id.partner_id
        vals['ubigeoPartida'] = sender_id.l10n_pe_district.code 
        vals['direccionPartida'] = sender_id.street
        vals['detalles'] = self._get_detalles_guia(picking_id.move_ids_without_package or picking_id.move_line_ids_without_package)
        print(vals)
        return vals
    
        
    def get_eguide_document(self, cpe_id):
        data = {}
        key = cpe_id.company_id.pe_private_key
        crt = cpe_id.company_id.pe_public_key
        if cpe_id._name=="pe.eguide":
            data = self._get_eguide_document(cpe_id.picking_id, key, crt)
        return data
    
    def send_eguide_document(self, cpe_id, xml = None):
        soap = {}
        soap['ruc'] = cpe_id.company_id.vat
        soap['usuario'] = cpe_id.company_id.pe_ws_user
        soap['clave'] = cpe_id.company_id.pe_ws_password
        soap['url'] =  cpe_id.company_id.pe_guide_ws_url
        soap['servidor'] =  cpe_id.company_id.pe_ws_server
        nombre_documento = cpe_id._pe_cpe_document_name(cpe_id.picking_id)
        vals = {}
        if cpe_id.company_id.pe_ws_server in ['nubefact_pse']:
            documento = Documento()
            documento.setDocument(self._get_eguide_document2(cpe_id.picking_id))
            data = documento.enviarDocumento(soap, nombre_documento, 'sync')
            vals.update(data)
        else:
            xml = xml or cpe_id.attachment_id.datas
            if not xml:
                val = self.get_eguide_document(cpe_id)
                vals.update(val)
                xml = vals.get('xml_firmado')
            documento = Documento()
            data = documento.enviarDocumento(soap, nombre_documento, 'sync', xml)
            vals.update(data)
        return vals
    