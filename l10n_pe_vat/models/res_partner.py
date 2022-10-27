# -*- encoding: utf-8 -*-
import requests
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from collections import OrderedDict
import re
import logging
_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _get_pe_doc_type(self):
        res = []
        res.append(('0', 'DOC.TRIB.NO.DOM.SIN.RUC'))
        res.append(('1', 'DOCUMENTO NACIONAL DE IDENTIDAD (DNI)'))
        res.append(('4', 'CARNET DE EXTRANJERIA'))
        res.append(('6', 'REGISTRO ÚNICO DE CONTRIBUYENTES'))
        res.append(('7', 'PASAPORTE'))
        res.append(('A', 'CÉDULA DIPLOMÁTICA DE IDENTIDAD'))
        res.append(('B', 'DOC.IDENT.PAIS.RESIDENCIA-NO.D'))
        res.append(('C', 'Tax Identifi cation Number - TIN – Doc Trib PP.NN'))
        res.append(('D', 'Identifi cation Number - IN – Doc Trib PP. JJ'))
        #res = self.env['pe.catalog.06'].get_selection()
        return res

    pe_doc_type= fields.Selection(selection=_get_pe_doc_type, string="Document Type")
    pe_doc_number= fields.Char(string="Document Number", compute = "_compute_pe_doc_number", inverse="_inverse_pe_doc_number")
    pe_commercial_name = fields.Char("Commercial Name", default="-", help='If you do not have a commercial name, put "-" without quotes')
    pe_legal_name = fields.Char("Legal Name", default="-", help='If you do not have a legal name, put "-" without quotes')
    
    pe_state = fields.Selection([('ACTIVO', 'ACTIVO'),
                            ('BAJA DE OFICIO', 'BAJA DE OFICIO'),
                            ('BAJA DEFINITIVA', 'BAJA DEFINITIVA'),
                            ('BAJA PROVISIONAL', 'BAJA PROVISIONAL'),
                            ('SUSPENSION TEMPORAL', 'BAJA PROVISIONAL'),
                            ('INHABILITADO-VENT.UN', 'INHABILITADO-VENT.UN'),
                            ('BAJA MULT.INSCR. Y O', 'BAJA MULT.INSCR. Y O'),
                            ('PENDIENTE DE INI. DE', 'PENDIENTE DE INI. DE'),
                            ('OTROS OBLIGADOS', 'OTROS OBLIGADOS'),
                            ('NUM. INTERNO IDENTIF', 'NUM. INTERNO IDENTIF'),
                            ('ANUL.PROVI.-ACTO ILI', 'ANUL.PROVI.-ACTO ILI'),
                            ('ANULACION - ACTO ILI', 'ANULACION - ACTO ILI'),
                            ('BAJA PROV. POR OFICI', 'BAJA PROV. POR OFICI'),
                            ('ANULACION - ERROR SU', 'ANULACION - ERROR SU')], "Sunat Status", default="ACTIVO")
    pe_condition = fields.Selection([('HABIDO', 'HABIDO'),
                                ('NO HABIDO', 'NO HABIDO'),
                                ('NO HALLADO', 'NO HALLADO'),
                                ('PENDIENTE', 'PENDIENTE'),
                                ('NO HALLADO SE MUDO D', 'NO HALLADO SE MUDO D'),
                                ('NO HALLADO NO EXISTE', 'NO HALLADO NO EXISTE'),
                                ('NO HALLADO FALLECIO', 'NO HALLADO FALLECIO'),
                                ('-', 'NO HABIDO'),
                                ('NO HALLADO OTROS MOT','NO HALLADO OTROS MOT'),
                                ('NO APLICABLE', 'NO APLICABLE'),
                                ('NO HALLADO NRO.PUERT', 'NO HALLADO NRO.PUERT'),
                                ('NO HALLADO CERRADO', 'NO HALLADO CERRADO'),
                                ('POR VERIFICAR', 'POR VERIFICAR'),
                                ('NO HALLADO DESTINATA', 'NO HALLADO DESTINATA'),
                                ('NO HALLADO RECHAZADO', 'NO HALLADO RECHAZADO')], 'Condition', default="HABIDO")
    
    #pe_activities_ids = fields.Many2many("pe.data.ciiu", string= "Economic Activities")
    #pe_main_activity = fields.Many2one("pe.data.ciiu", string= "Main Economic Activity")
    pe_retention_agent = fields.Boolean("Is Agent")
    pe_retention_agent_from = fields.Date("From")
    pe_retention_agent_resolution = fields.Char("Resolution")
    pe_is_validate= fields.Boolean("Is Validated")
    pe_type_taxpayer = fields.Char("Type Taxpayer")
    pe_emission_system = fields.Char("Emission System")
    pe_accounting_system = fields.Char("Accounting System")
    pe_last_update = fields.Date("Last Update")
    pe_representative_ids = fields.One2many("pe.res.partner.representative", "partner_id", "Representatives")
    
    @api.depends('vat')
    def _compute_pe_doc_number(self):
        for partner in self:
            partner.pe_doc_number = partner.vat
    
    @api.depends('pe_doc_number')
    def _inverse_pe_doc_number(self):
        for partner in self:
            partner.vat = partner.pe_doc_number
    
    @api.onchange('pe_doc_number')
    def _onchange_pe_doc_number(self):
        self.vat = self.pe_doc_number
    
    @api.onchange('pe_doc_type')
    def onchange_pe_doc_type(self):
        if self.pe_doc_type:
            if self.pe_doc_type == '0':
                self.l10n_latam_identification_type_id = self.env.ref('l10n_pe.it_NDTD').id or False
            elif self.pe_doc_type == '1':
                self.l10n_latam_identification_type_id = self.env.ref('l10n_pe.it_DNI').id or False
            elif self.pe_doc_type == '4':
                self.l10n_latam_identification_type_id = self.env.ref('l10n_latam_base.it_fid').id or False
            elif self.pe_doc_type == '6':
                self.l10n_latam_identification_type_id = self.env.ref('l10n_pe.it_RUC').id or False
            elif self.pe_doc_type == '7':
                self.l10n_latam_identification_type_id = self.env.ref('l10n_latam_base.it_pass').id or False
            elif self.pe_doc_type == 'A':
                self.l10n_latam_identification_type_id = self.env.ref('l10n_pe.it_DIC').id or False
            elif self.pe_doc_type == 'B':
                self.l10n_latam_identification_type_id = self.env.ref('l10n_pe.it_IDCR').id or False
            elif self.pe_doc_type == 'C':
                self.l10n_latam_identification_type_id = self.env.ref('l10n_pe.it_TIN').id or False
            elif self.pe_doc_type == 'D':
                self.l10n_latam_identification_type_id = self.env.ref('l10n_pe.it_IN').id or False
            else:
                self.l10n_latam_identification_type_id = self.env.ref('l10n_pe.it_NDTD').id
        else:
            self.l10n_latam_identification_type_id = self.env.ref('l10n_pe.it_NDTD').id
            
    def check_vat_pe(self, vat):
        return True      
    
    @api.constrains("vat", "pe_doc_type")
    def check_doc_number(self):
        for partner in self:
            vat = partner.vat or partner.pe_doc_number
            if partner.parent_id:
                continue
            if not partner.pe_doc_type and not vat:
                continue
            elif not partner.pe_doc_type and vat:
                raise ValidationError(_("Select a document type"))
            elif partner.pe_doc_type and not vat:
                raise ValidationError(_("Enter the document number"))
            if partner.pe_doc_type == '6':
                check = self.validate_ruc(vat)
                if not check:
                    _logger.info("The RUC Number [%s] is not valid !" % vat)
                    raise ValidationError(_('the RUC entered is incorrect'))
            elif partner.pe_doc_type == '0':
                if len(vat)>15 or not vat.isalnum():
                    _logger.info("The OTROS Number [%s] is not valid !" % vat)
                    raise ValidationError(_('the OTROS entered is incorrect'))
            elif partner.pe_doc_type == '1':
                check = self.validate_dni(vat)
                if not check:
                    _logger.info("The DNI Number [%s] is not valid !" % vat)
                    raise ValidationError(_('the DNI entered is incorrect'))
            elif partner.pe_doc_type == '4':
                if len(vat)>12 or not vat.isalnum():
                    _logger.info("The CARNET DE EXTRANJERIA Number [%s] is not valid !" % vat)
                    raise ValidationError(_('the CARNET DE EXTRANJERIA entered is incorrect'))
            elif partner.pe_doc_type == '7':
                if len(vat)>12 or not vat.isalnum():
                    _logger.info("The PASAPORTE Number [%s] is not valid !" % vat)
                    raise ValidationError(_('the PASAPORTE entered is incorrect'))
            elif partner.pe_doc_type == 'A':
                if len(vat)>15 or not vat.isdigit():
                    _logger.info("The CEDULA DIPLOMATICA Number [%s] is not valid !" % vat)
                    raise ValidationError(_('the CEDULA DIPLOMATICA entered is incorrect'))
            if self.search_count([('company_id','=', partner.company_id.id),
                                  ('pe_doc_type', '=', partner.pe_doc_type), ('vat', '=', partner.vat)])>1:
                _logger.info('Document Number already exists and violates unique field constrain')
                raise ValidationError(_('Document Number already exists and violates unique field constrain'))

    @api.onchange('company_type')
    def onchange_company_type(self):
        self.pe_doc_type= self.company_type == 'company' and "6" or "1"
        super(Partner, self).onchange_company_type()
    
    @staticmethod
    def validate_dni(vat):
        if len(vat) != 8:
            return False
        if not vat.isdigit():
            return False
        return True
    
    @staticmethod
    def validate_ruc(vat):
        factor = '5432765432'
        sum = 0
        dig_check = False
        if len(vat) != 11:
            return False
        try:
            int(vat)
        except ValueError:
            return False 
        for f in range(0,10):
            sum += int(factor[f]) * int(vat[f])
        subtraction = 11 - (sum % 11)
        if subtraction == 10:
            dig_check = 0
        elif subtraction == 11:
            dig_check = 1
        else:
            dig_check = subtraction
        if not int(vat[10]) == dig_check:
            return False
        return True
    
    @api.onchange("pe_doc_number", "pe_doc_type")
    @api.depends("pe_doc_type", "pe_doc_number")
    def _doc_number_change(self):
        vat=self.pe_doc_number
        warning = {}
        res = {}
        if vat and self.pe_doc_type:
            vat_type = self.pe_doc_type
            reponse = True
            if vat_type == '1':
                if len(vat)!=8:
                    warning = {
                            'title': _("Warning for %s") % vat,
                            'message':_('the DNI entered is incorrect')
                        }
                    return {'warning': warning}
                try:
                    company = self.env.user.company_id
                    if company.l10n_pe_api_dni_connection == 'facturacion_electronica':
                        response = requests.get("http://api.grupoyacck.com/dni/%s/" % vat.strip(), timeout = 300)
                    if company.l10n_pe_api_dni_connection == 'free_api':
                        response = requests.get("https://api.apis.net.pe/v1/dni?numero=%s" % vat.strip(), timeout = 300)
                except Exception:
                    reponse=False
                if response and response.status_code!=200:
                    vals= {'detail':"Not found."}
                else:
                    vals = response and response.json() or {'detail':"Not found."}
                if vals and vals.get('detail') != 'Not found.':
                    if self.env.user.company_id.l10n_pe_api_dni_connection == 'free_api':
                        vals['paternal_surname'] = vals.get('apellidoPaterno', '')
                        vals['maternal_surname'] = vals.get('apellidoMaterno', '')
                        vals['name'] = vals.get('nombres', '')
                    if vals.get('paternal_surname', '') and vals.get('maternal_surname', '') and vals.get('name', ''):
                        self.name= "%s %s, %s" %(vals.get('paternal_surname', ''), vals.get('maternal_surname', ''), vals.get('name', ''))
                        self.pe_is_validate = True
                self.company_type="person"
            elif vat_type=="6":
                if not self.validate_ruc(vat):
                    warning = {
                            'title': _("Warning for %s") % vat,
                            'message':_('the RUC entered is incorrect')
                        }
                    return {'warning': warning}
                response = False
                try:
                    company = self.env.user.company_id
                    if company.l10n_pe_api_dni_connection == 'facturacion_electronica':
                        if self.env.context.get('force_update'):
                            response = requests.get("http://api.grupoyacck.com/ruc/%s/?force_update=1" % vat.strip())
                        else:
                            response = requests.get("http://api.grupoyacck.com/ruc/%s/" % vat.strip())
                    if company.l10n_pe_api_dni_connection == 'free_api':
                        response = requests.get("https://api.apis.net.pe/v1/ruc?numero=%s" % vat.strip(), timeout = 300)
                except Exception:
                    reponse=False
                vals = response and response.status_code==200 and response.json() or {'detail':"Not found."}
                if vals.get('detail', '') == "Not found.":
                    warning = {
                            'title': _("Warning for %s") % vat,
                            'message':_('RUC not found, try checking again')
                        }
                    return {'warning': warning}
                if vals:
                    if self.env.user.company_id.l10n_pe_api_dni_connection == 'free_api':
                        vals['commercial_name'] = '-'
                        vals['legal_name'] = vals.get('nombre')
                        vals['street'] = vals.get('direccion')
                        vals['state'] = vals.get('estado')
                        vals['condition'] = vals.get('condicion')
                        
                    self.pe_commercial_name = vals.get('commercial_name', False)
                    self.pe_legal_name = vals.get('legal_name', False)
                    self.name = vals.get('legal_name') or  vals.get('name') or False                    
                    self.street = vals.get('street', False)
                    self.company_type="company"                    
                    self.pe_state = vals.get('state', False)
                    self.pe_condition = vals.get('condition', False)
                    self.pe_type_taxpayer = vals.get('type_taxpayer', False)
                    self.pe_emission_system = vals.get('emission_system', False)
                    self.pe_accounting_system = vals.get('accounting_system', False)
                    try:
                        self.pe_last_update = vals.get('last_update') and fields.Datetime.context_timestamp(self, datetime.strptime(vals.get('last_update'), '%Y-%m-%dT%H:%M:%S.%fZ')) or False
                    except Exception:
                        pass
                    self.pe_is_validate = True
                    if vals.get('activities'):
                        activities_ids = []
                        for activity in  vals.get('activities'):
                            ciiu = self.env['pe.catalog.ciiu'].search([('code', '=', activity.get('code'))], limit=1)
                            if ciiu:
                                activities_ids.append(ciiu.id)
                            else:
                                ciiu = self.env['pe.catalog.ciiu'].sudo().create(activity)
                                activities_ids.append(ciiu.id)
                        if activities_ids:
                            self.pe_main_activity = activities_ids[-1]
                            if self.pe_activities_ids:
                                self.pe_activities_ids = [(6, None, activities_ids)]
                            else:
                                act=[]
                                for activity_id in activities_ids:
                                    act.append((4,activity_id))
                                self.pe_activities_ids = act
                    if vals.get('representatives'):
                        representatives=[]
                        for rep in vals.get('representatives'):
                            representatives.append((0, None,rep))
                        self.pe_representative_ids = representatives
                    self.pe_retention_agent = vals.get('retention_agent', False)
                    self.pe_retention_agent_from = vals.get('retention_agent_from', False)
                    self.pe_retention_agent_resolution = vals.get('retention_agent_resolution', False)
                    if vals.get('ubigeo'):
                        district = self.env['l10n_pe.res.city.district'].search([('code','=', vals.get('ubigeo'))], limit = 1)
                        if len(district)==1:
                            self.l10n_pe_district=district.id
                            self.city_id = district.city_id.id
                            self.state_id = district.city_id.state_id.id
                    child_ids = []
                    for child_id in self.child_ids:
                        child_ids.append((1,child_id.id, {'pe_doc_type':self.pe_doc_type, 'vat':vat}))
                    self.child_ids = child_ids
        return {'warning': warning}

    def write(self, vals):
        for partner_id in self:
            if partner_id.pe_representative_ids and vals.get('pe_representative_ids'):
                partner_id.pe_representative_ids.unlink()
        return  super(Partner, self).write(vals)
    
    @api.model
    def change_commercial_name(self):
        partner_ids=self.search([('commercial_name', '!=', '-'), ('pe_doc_type', '=', '6')])
        partner_ids.update_document()

    def update_document(self):
        for partner in self:
            partner._doc_number_change()

    @api.model
    def update_partner_datas(self):
        partner_ids = self.search([('pe_doc_type', '=', '6')])
        for partner in partner_ids:
            partner.name = partner.commercial_name

    @api.model
    def get_partner_from_ui(self, doc_type=None, doc_number=None):
        url=None
        res={}
        if doc_type=="1":
            url = "http://api.grupoyacck.com/dni/%s/" % doc_number
        elif doc_type=="6":
            url = "http://api.grupoyacck.com/ruc/%s/?force_update=1" % doc_number
        if url:
            try:
                response = requests.get(url)
            except Exception:
                reponse=False
            if response and response.status_code==200:
                vals = response and response.json() or {'detail':"Not found."}
                res = vals
        # if res.get('district') and res.get('province'):
        #     district = self.env['l10n_pe.res.city.district'].search([('name','ilike', res.get('district')),
        #                                                            ('city_id.name','ilike', res.get('province'))])
        #     if len(district)==1:
        #         res['l10n_pe_district']=district.id
        #         res['city_id'] = district.city_id.id
        #         res['state_id'] = district.city_id.state_id.id
        #         res['city'] = district.name
        #         res['zip'] = district.code
        if res.get('ubigeo'):
            district = self.env['l10n_pe.res.city.district'].search([('code','=', res.get('ubigeo'))])
            if len(district)==1:
                res['l10n_pe_district']=district.id
                res['city_id'] = district.city_id.id
                res['state_id'] = district.city_id.state_id.id
                res['city'] = district.name
                res['zip'] = district.code
        res['country_id'] = self.env.ref('base.pe').id
        return res
class PartnerRepresentative(models.Model):
    _name = "pe.res.partner.representative"
    _description = 'Peruvian supplier representative'

    name = fields.Char("Name")
    doc_type = fields.Char("Document Type")
    doc_number = fields.Char("Document Number")
    position = fields.Char("Position")
    date_from = fields.Date("Date From")
    partner_id = fields.Many2one("res.partner", "Partner")
    
    
