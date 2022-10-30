odoo.define('l10n_uy_edi_pos.PosResPaymentScreen', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    const PosResPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            async validateOrder(isForceValidate) {
                this.currentOrder.set_to_invoice(true);
                if (!this.currentOrder.get_client() && this.env.pos.config.default_partner_id){
                    var new_client = this.env.pos.db.get_partner_by_id(this.env.pos.config.default_partner_id[0]);
                    if (new_client){
                        this.currentOrder.set_client(new_client);    
                    }
                }
                return await super.validateOrder(isForceValidate);
            }
        };

    Registries.Component.extend(PaymentScreen, PosResPaymentScreen);

    return PosResPaymentScreen;
});
