odoo.define('l10n_pe_pos_cpe.PosResPaymentScreen', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    const PosResPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            async validateOrder(isForceValidate) {
                var order = this.currentOrder;
                if (!order.is_to_invoice() && order.get_pe_move_name()){
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('There is assigned number'),
                        body: this.env._t("This order has an assigned number and must be sent as electronic proof "),
                    });
                    return;
                }
                if (order.is_to_invoice() && this.env.pos.company.pe_max_amount>700.0 && !order.get_pe_doc_type()){
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Customer document error '),
                        body: this.env._t("Assign another customer with identification number "),
                    });
                    return;
                }

                if (order.is_to_invoice() && !order.get_pe_journal_id() && order.get_client()){
                    order.calculate_pe_document_type();
                }
                if(order.is_to_invoice() && order.get_pe_journal_id() && !order.get_pe_move_name()){
                    var number = this.env.pos.get_pe_move_name(order.get_pe_journal_id());
                    order.set_pe_move_name(number.pe_move_name);
                }
                if (order.get_pe_move_name()){
                    var blob = new Blob([JSON.stringify(order.export_as_JSON())], {type: "text/plain;charset=utf-8"});
                    saveAs(blob, order.get_pe_move_name()+".json");    
                }
                return await super.validateOrder(isForceValidate);
            }
        };

    Registries.Component.extend(PaymentScreen, PosResPaymentScreen);

    return PosResPaymentScreen;
});
