# -*- coding: utf-8 -*-
from io import BytesIO
import zipfile
from odoo import fields, models, _
from odoo.exceptions import ValidationError
from base64 import decodestring, decodebytes, encodebytes

class CpeXMLBkWizard(models.TransientModel):
    _name = 'cpe.xml.bk.wizard'
    _description = 'XML Backup'
    
    file_name = fields.Char("File Name")
    file_data = fields.Binary("XML Backup")
    start_date = fields.Date("Start Date", required=True)
    end_date = fields.Date("End Date", required=True)
    
    def download_bk(self):
        self.ensure_one()
        if self.start_date.strftime("%Y%m") != self.end_date.strftime("%Y%m"):
            raise ValidationError(_("The copy must be in the same month"))
        zip_data = BytesIO()
        zip_file = zipfile.ZipFile(zip_data, "w", zipfile.ZIP_DEFLATED, False)
        cpe_ids = self.env['account.edi.document'].search([('pe_date','>=',self.start_date),
                                             ('pe_date','<=',self.end_date),('state','=','sent')])
        
        for cpe_id in cpe_ids:
            if cpe_id.attachment_id and cpe_id.attachment_id.datas:
                zip_file.writestr(cpe_id.attachment_id.name, decodebytes(cpe_id.attachment_id.datas))
            if cpe_id.pe_response_id and cpe_id.pe_response_id.datas:
                zip_file.writestr(cpe_id.pe_response_id.name, decodebytes(cpe_id.pe_response_id.datas))
        
        cpe_ids = self.env['pe.cpe.rc'].search([('pe_date','>=',self.start_date),
                                             ('pe_date','<=',self.end_date),('state','=','sent')])
        for cpe_id in cpe_ids:
            if cpe_id.attachment_id and cpe_id.attachment_id.datas:
                zip_file.writestr(cpe_id.attachment_id.name, decodebytes(cpe_id.attachment_id.datas))
            if cpe_id.pe_response_id and cpe_id.pe_response_id.datas:
                zip_file.writestr(cpe_id.pe_response_id.name, decodebytes(cpe_id.pe_response_id.datas))
        
        cpe_ids = self.env['pe.cpe.ra'].search([('pe_date','>=',self.start_date),
                                             ('pe_date','<=',self.end_date),('state','=','sent')])
        for cpe_id in cpe_ids:
            if cpe_id.attachment_id and cpe_id.attachment_id.datas:
                zip_file.writestr(cpe_id.attachment_id.name, decodebytes(cpe_id.attachment_id.datas))
            if cpe_id.pe_response_id and cpe_id.pe_response_id.datas:
                zip_file.writestr(cpe_id.pe_response_id.name, decodebytes(cpe_id.pe_response_id.datas))
        
        for zfile in zip_file.filelist:
            zfile.create_system = 0
        zip_file.close()
        res = zip_data.getvalue()
        path = "/web/cpe/download_file?"
        self.file_name = self.start_date.strftime("%Y%d")
        self.file_data = encodebytes(res)
        url = path + "model={}&id={}&filename={}.zip".format(
            self._name, self.id, self.file_name)
    
        return {
            'type' : 'ir.actions.act_url',
            'url': url,
            'target': 'self',
            'tag': 'reload',
        }