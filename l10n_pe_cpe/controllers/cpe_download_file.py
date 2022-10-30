
from odoo import http, _
from odoo.http import request, content_disposition, route
from odoo.addons.web.controllers.main import serialize_exception
import base64

class CpeDownload(http.Controller):
    
    @route('/web/cpe/download_file', type='http', auth="user")
    @serialize_exception
    def cpe_download_file(self, model, id, filename=None, **kw):
        record = request.env[model].browse(int(id))
        
        binary_file = record.file_data # aqui colocas el nombre del campo binario que almacena tu archivo
        filecontent = base64.b64decode(binary_file or '')
        content_type, disposition_content = False, False

        if not filecontent:
            return request.not_found()
        else:
            if not filename:
                filename = '%s.zip' % (record.start_date.strftime("%Y%m"))
            content_type = ('Content-Type', 'application/zip')
            disposition_content = ('Content-Disposition', content_disposition(filename))

        return request.make_response(filecontent, [content_type,
                                                   disposition_content])