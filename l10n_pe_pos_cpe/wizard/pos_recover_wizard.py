# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json
from base64 import b64decode

class PePosRecoverWizard(models.TransientModel):
    _name = "pe.pos.recover.wizard"
    
    name = fields.Char("Number")
    fname = fields.Char("File Name")
    fdatas = fields.Binary("Json Invoice")
    session_id = fields.Many2one('pos.session', string='Session', domain="[('state', '=', 'opened')]")
    is_new = fields.Boolean("Is New")
    
    @api.multi
    def check_invoice_number(self):
        self.ensure_one()
        if self.name:
            if self.env['account.invoice'].search([('move_name','=',self.name)]):
                raise ValidationError(_("It is not a json file"))
        return True
    
    @api.multi
    def get_fdatas(self):
        self.ensure_one()
        res = False
        if self.fdatas:
            try:
                res = json.loads(str(b64decode(self.fdatas),'utf-8'))
            except Exception:
                raise ValidationError(_("It is not a json file"))
        #else:
        #    raise ValidationError(_("There is no data to process"))
        return res
    
    @api.onchange('fdatas')
    def onchange_fdatas(self):
        res = self.get_fdatas()
        if res:
            self.name = res.get('number', False)
            self.session_id = res.get("pos_session_id", False)
            self.check_invoice_number()
    
    @api.multi
    def action_view_pos_order(self, order_id):
        self.ensure_one()
        action = self.env.ref('point_of_sale.action_pos_pos_form').read()[0]
        if order_id:
            action['views'] = [(self.env.ref('point_of_sale.view_pos_pos_form').id, 'form')]
            action['res_id'] = order_id[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    def _default_session(self):
        session_id = self.env['pos.session'].search([('state', '=', 'opened'), ('user_id', '=', self.env.uid)], limit=1)
        if not session_id:
            session_id = self.env['pos.session'].search([('state', '=', 'opened')], limit=1)
        return session_id
    
    @api.multi
    def create_order(self):
        self.ensure_one()
        res = self.get_fdatas()
        res['number'] = self.name
        if self.is_new:
            vals = {}
            if self.session_id.state == 'opened':
                res["session_id"] = self.session_id.id
            else:
                res["session_id"] = self._default_session().id
            self.check_invoice_number()
            vals['date_invoice'] = res.get("date_invoice")
            
            vals['partner_id'] = res.get("partner_id", False)
            vals['pricelist_id'] = res.get("pricelist_id", False)
            vals['user_id'] = res.get("user_id")
            vals['sequence_number'] = res.get("sequence_number")
            vals['fiscal_position_id'] = res.get("fiscal_position_id")
            vals['invoice_journal'] = res.get("invoice_journal")
            vals['number'] = res.get("number")
            vals['pe_invoice_date'] = res.get("pe_invoice_date")
            vals['lines'] = res.get("lines")
            order_id = self.env['pos.order'].create(vals)
        else:
            res["pos_session_id"] = self.session_id.id
            self.check_invoice_number()
            orders = [{'id':res['uid'],'data':res}]
            order_id = self.env['pos.order'].create_from_ui(orders)
        return self.action_view_pos_order(order_id)
        
    