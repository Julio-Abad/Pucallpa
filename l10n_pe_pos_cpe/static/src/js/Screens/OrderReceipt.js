odoo.define('l10n_pe_pos_cpe.PosResOrderReceipt', function (require) {
    'use strict';

    const OrderReceipt = require('point_of_sale.OrderReceipt');
    const Registries = require('point_of_sale.Registries');

    const PosResOrderReceipt = (OrderReceipt) =>
        class extends OrderReceipt {
            willUpdateProps(nextProps) {
                var qr_string = this.props.order.get_cpe_qr()
                if (this.props.order.get_cpe_type()){
                    var qrcode = new QRCode(document.getElementById("qr-code"), { width : 128, height : 128, correctLevel : QRCode.CorrectLevel.Q });
                    qrcode.makeCode(qr_string);
                }
                return super.willUpdateProps(nextProps);
            }
        };

    Registries.Component.extend(OrderReceipt, PosResOrderReceipt);

    return PosResOrderReceipt;
});
