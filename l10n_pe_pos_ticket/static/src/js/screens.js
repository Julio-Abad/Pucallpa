odoo.define('l10n_pe_pos_ticket.screens', function (require) {
	var screens = require('point_of_sale.screens');
	var core = require('web.core');
	var QWeb = core.qweb;
	var _t = core._t;
	
	screens.ReceiptScreenWidget.include({
        render_receipt: function() {
            var self = this;
            this._super();
            var order = this.pos.get('selectedOrder');
            this.$('.pos-receipt-container').html(QWeb.render('PosTicketPeruvianModel01', this.get_receipt_render_env()));
            if (order.get_cpe_type()){
                var qr_string=order.get_cpe_qr(); 
                var qrcode = new QRCode(document.getElementById("qr-code"), { width : 128, height : 128, correctLevel : QRCode.CorrectLevel.Q });
                qrcode.makeCode(qr_string);
            }
        },
	});

});