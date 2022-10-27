# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import re
from io import BytesIO
from base64 import encodestring
import qrcode
try:
    qr_mod = True
except:
    qr_mod = False

class Picking(models.Model):
    _inherit = "stock.picking"
    
    #pe_voided_id = fields.Many2one("pe.eguide", "Guide canceled", copy=False)
    pe_guide_number = fields.Char("Guide Number", default="/", copy=False)
    pe_is_realeted = fields.Boolean("Is Related", copy=False)
    pe_related_number = fields.Char("Related Number", copy=False)
    pe_related_code = fields.Selection(selection="_get_pe_related_code", string="Related Number", copy=False)
    pe_supplier_id = fields.Many2one(comodel_name="res.partner", string="Supplier", copy=False)
    pe_transfer_code = fields.Selection(selection="_get_pe_transfer_code", string="Transfer code", default="01", copy=False)
    pe_gross_weight = fields.Float("Gross Weigh", digits='Product Unit of Measure', copy=False)
    pe_unit_quantity = fields.Integer("Unit Quantity", copy=False)
    pe_transport_mode = fields.Selection(selection="_get_pe_transport_mode", string="Transport Mode", copy=False)
    pe_carrier_id = fields.Many2one(comodel_name="res.partner", string="Carrier", compute="_compute_pe_carrier_id", inverse="_inverse_pe_carrier_id")
    pe_is_eguide = fields.Boolean("Is EGuide", copy=False)
    pe_is_programmed = fields.Boolean("Transfer Programmed", copy=False)
    pe_date_issue = fields.Date('Date Issue', copy=False)
    pe_fleet_ids = fields.One2many(comodel_name="pe.stock.fleet", inverse_name="picking_id", string="Fleet Private", copy=False)
    
    pe_guide_ids = fields.One2many("pe.eguide", 'picking_id', "Guides Electronic", copy=False)
    
    pe_guide_id = fields.Many2one("pe.eguide", "Guide Electronic", compute = "_compute_pe_eguide_detail", store=True, copy=False)
    pe_digest = fields.Char("Digest", compute = "_compute_pe_eguide_detail", store=True, copy=False)
    pe_response = fields.Char("Response", compute = "_compute_pe_eguide_detail", store=True, copy=False)
    pe_return_code = fields.Selection("_get_return_code", string= "Return Code",  compute="_compute_pe_eguide_detail", store=True, copy=False)
    pe_note = fields.Char(string= "Return Code",  compute="_compute_pe_eguide_detail", store=True, copy=False)
    pe_response_id = fields.Many2one("ir.attachment", "XML", compute="_compute_pe_eguide_detail", store=True, copy=False)
    pe_attachment_id = fields.Many2one("ir.attachment", "XML Response", compute="_compute_pe_eguide_detail", store=True, copy=False)
    
    pe_qr_code = fields.Binary("Qr Code", compute="_compute_pe_qr_code")
    
    pe_return_code = fields.Selection("_get_return_code", string= "Return Code",  readonly=True)
    pe_carrier_ids = fields.Many2many('res.partner', 'stock_picking_pe_carrier_rel', 'stock_id', 'partner_id', "Carriers", copy=False)
    
    @api.depends('pe_guide_ids.pe_digest',
                 'pe_guide_ids.pe_response',
                 'pe_guide_ids.pe_return_code',
                 'pe_guide_ids.pe_response_id',
                 'pe_guide_ids.attachment_id')
    def _compute_pe_eguide_detail(self):
        for picking_id in self:
            pe_guide_ids = picking_id.pe_guide_ids
            pe_guide_id = pe_guide_ids and pe_guide_ids[0] or False
            picking_id.pe_guide_id = pe_guide_id and pe_guide_id[0] or False
            picking_id.pe_digest = pe_guide_id and  pe_guide_id.pe_digest or False
            picking_id.pe_response = pe_guide_id and  pe_guide_id.pe_response or False
            picking_id.pe_return_code = pe_guide_id and pe_guide_id.pe_return_code or False
            picking_id.pe_response_id = pe_guide_id and pe_guide_id.pe_response_id.id or False
            picking_id.pe_attachment_id = pe_guide_id and pe_guide_id.attachment_id.id or False
            picking_id.pe_note = pe_guide_id and pe_guide_id.pe_note or False
    
    @api.depends('pe_carrier_ids','pe_transport_mode')
    def _compute_pe_carrier_id(self):
        for stock_id in self:
            pe_carrier_id = False
            for pe_carrier in stock_id.pe_carrier_ids:
                pe_carrier_id = pe_carrier.id
                break
            stock_id.pe_carrier_id = pe_carrier_id
            
    @api.depends('pe_carrier_id','pe_transport_mode')
    def _inverse_pe_carrier_id(self):
        for stock_id in self:
            if stock_id.pe_transport_mode in ['01']:
                stock_id.pe_carrier_ids = [(6,0,stock_id.pe_carrier_id.ids)]
    
    @api.model
    def _get_return_code(self):
        return self.env['pe.catalog.return'].get_selection()
    
    @api.model
    def _get_pe_transport_mode(self):
        return self.env['pe.catalog.18'].get_selection()
    
    @api.model
    def _get_pe_related_code(self):
        return self.env['pe.catalog.21'].get_selection()

    @api.model
    def _get_pe_transfer_code(self):
        return self.env['pe.catalog.20'].get_selection()
    
    def action_cancel_eguide(self):
        for picking_id in self:
                if picking_id.pe_guide_id and picking_id.pe_guide_id.state not in ["draft", "generate", "cancel"]:
                    voided_id = self.env['pe.eguide'].get_eguide_async('low', picking_id)
                    picking_id.pe_voided_id = voided_id.id
    
    def _compute_pe_qr_code(self):
        for picking_id in self:
            res=[]
            if picking_id.pe_guide_number and picking_id.pe_is_eguide and qr_mod:
                res.append(picking_id.company_id.partner_id.pe_doc_number)
                res.append('09')
                res.append(picking_id.pe_guide_number.split("-")[0] or '')
                res.append(picking_id.pe_guide_number.split("-")[1] or '')
                res.append(fields.Date.to_string(picking_id.pe_date_issue))
                res.append(picking_id.partner_id.pe_doc_type or "-")
                res.append(picking_id.partner_id.pe_doc_number or "-")
                #res.append(picking_id.pe_digest or "")
                res.append("")
                qr_string='|'.join(res)
                qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_Q)
                qr.add_data(qr_string)
                qr.make(fit=True)
                image = qr.make_image()
                tmpf = BytesIO()
                image.save(tmpf,'png')
                picking_id.pe_qr_code = encodestring(tmpf.getvalue())
    
    def do_new_transfer(self):
        res=super(Picking, self).do_new_transfer()
        self.pe_gross_weight=sum([line.product_id.weight for line in self.pack_operation_ids])
        self.pe_unit_quantity= sum([line.qty_done or line.product_qty for line in self.pack_operation_ids])
        return res

    def validate_eguide(self):
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_("Customer is required"))
        if self.partner_id.id == self.company_id.partner_id.id and self.pe_transfer_code in ["02", "04"]:
            raise UserError("Destinatario no debe ser igual al remitente")
        if not self.partner_id.parent_id.pe_doc_type and not self.partner_id.pe_doc_type:
            raise UserError(_("Customer type document is required"))
        if not self.partner_id.parent_id.pe_doc_number and not self.partner_id.pe_doc_number:
            raise UserError(_("Customer number document is required"))
        if not self.partner_id.street:
            raise UserError(_("Customer street is required for %s") %(self.partner_id.name or ""))
        if not self.partner_id.l10n_pe_district:
            raise UserError(_("Customer district is required for %s")  %(self.partner_id.name or ""))
        
        if not self.pe_carrier_id.pe_doc_type and self.pe_transport_mode=="01":
            raise UserError(_("Carrier type document is required for %s") %(self.pe_carrier_id.name or ""))
        if not self.pe_carrier_id.pe_doc_number and self.pe_transport_mode=="01":
            raise UserError(_("Carrier number document is required for %s") %(self.pe_carrier_id.name or ""))
        if not self.picking_type_id.warehouse_id.partner_id or not self.picking_type_id.warehouse_id.partner_id.street:
            raise UserError(_("It is necessary to enter the warehouse address for %s") %(self.picking_type_id.warehouse_id.partner_id.name or ""))
        if self.picking_type_id.warehouse_id.partner_id and not self.picking_type_id.warehouse_id.partner_id.l10n_pe_district:
            raise UserError(_("It is necessary to enter the warehouse district for %s") %(self.picking_type_id.warehouse_id.partner_id.name or ""))
        if self.pe_carrier_ids:
            for partner_id in self.pe_carrier_ids:
                if not partner_id.pe_doc_type:
                    raise UserError(_("Carrier type document is required for %s") %(partner_id.name or ""))
                if not partner_id.pe_doc_number:
                    raise UserError(_("Carrier number document is required for %s") %(partner_id.name or ""))
        if self.pe_transport_mode=="02" and not self.pe_fleet_ids:
            raise UserError(_("It is necessary to add a vehicle and driver"))

    def action_generate_eguide(self):
        for stock in self:
            if stock.pe_is_eguide:
                self.validate_eguide()
                self.pe_date_issue = fields.Date.context_today(self)
                if stock.pe_guide_number=='/':
                    if stock.picking_type_id.warehouse_id.pe_sequence_id:
                        stock.pe_guide_number=stock.picking_type_id.warehouse_id.pe_sequence_id.next_by_id()
                    else:
                        stock.pe_guide_number = self.env['ir.sequence'].next_by_code('pe.eguide.sync')
                if not re.match(r'^(T){1}[A-Z0-9]{3}\-\d+$', stock.pe_guide_number):
                    raise UserError("El numero de la guia ingresada no cumple con el estandar.\n"\
                                    "Verificar la secuencia del Diario por jemplo T001- o TG01-. \n"\
                                    "Para cambiar ir a Configuracion/Gestion de Almacenes/Almacenes")
                #if not self.pe_guide_id:
                pe_guide_id = self.env['pe.eguide'].create_from_stock(stock)
                #    stock.pe_guide_id = pe_guide_id.id
                #else:
                #    pe_guide_id=stock.pe_guide_id
                if stock.company_id.pe_is_sync:
                    #pe_guide_id.action_generate()
                    pe_guide_id.action_sent()
                else:
                    pe_guide_id.action_generate()
                #self.pe_number = stock.pe_guide_number    

class PeStockFleet(models.Model):
    _name = "pe.stock.fleet"
    
    name = fields.Char("License Plate", required=True)
    fleet_id = fields.Many2one(comodel_name="fleet.vehicle", string="Vehicle")
    picking_id = fields.Many2one(comodel_name="stock.picking", string="Picking")
    #driver_id = fields.Many2one(comodel_name="res.partner", string="Driver", required=True)
    is_main = fields.Boolean("Main")
    
    @api.onchange("fleet_id")
    def onchange_fleet_id(self):
        if self.fleet_id:
            self.name = self.fleet_id.license_plate
            #self.driver_id = self.fleet_id.driver_id.id
            
class Warehouse(models.Model):
    _inherit = "stock.warehouse"
    
    pe_sequence_id = fields.Many2one('ir.sequence', 'Eguide Sequence', )
