odoo.define('l10n_pe_pos.PosResClientDetailsEdit', function (require) {
    'use strict';
    const { _t } = require('web.core');
    const ClientDetailsEdit = require('point_of_sale.ClientDetailsEdit');
    const Registries = require('point_of_sale.Registries');
    const rpc = require('web.rpc');

    const PosResClientDetailsEdit = (ClientDetailsEdit) =>
        class extends ClientDetailsEdit {
            constructor() {
                super(...arguments);

            }
            captureChange(event){
                super.captureChange(event);
                var pe_doc_type = this.changes['pe_doc_type'];
                var vat = this.changes['vat']
                var sself = this;
                if (this.changes['pe_doc_type']=='6') {
                    self.$('.partner-pe-condition').show();
                    self.$('.partner-pe-state').show();
                    
                } else {
                    self.$('.partner-pe-condition').hide();
                    self.$('.partner-pe-state').hide();
                }
                if(this.changes['pe_doc_type'] && this.changes['vat']) {
                    if(!this.env.pos.validate_pe_doc(pe_doc_type, vat)){
                        return this.showPopup('ErrorPopup', {
                          title: _t('The document number is invalid'),
                        });
                    }
                    else if(['1', '6'].indexOf(pe_doc_type)!=-1){
                        rpc.query({
                        model: 'res.partner',
                        method: 'get_partner_from_ui',
                        args: [pe_doc_type, vat],
                        }, {
                            timeout: 7500,
                        })
                        .then(function (result) {
                            if (result.detail!="Not found."){
                                if (pe_doc_type == "1"){
                                    self.$("[name='name']").val(result.paternal_surname+' '+result.maternal_surname+', '+ result.name);
                                    self.$('.pe_is_validate').val(true);//attr('checked', true);
                                    self.$('.pe_last_update').val(result.last_update);
                                    sself.changes['name'] = result.paternal_surname+' '+result.maternal_surname+', '+ result.name;
                                    sself.changes['pe_is_validate'] = true;
                                    sself.changes['pe_last_update'] = result.last_update;
                                }
                                else if (pe_doc_type == "6"){
                                    self.$("[name='name']").val(result.legal_name);
                                    self.$('.pe_commercial_name').val(result.commercial_name);
                                    self.$('.pe_legal_name').val(result.legal_name);
                                    self.$("[name='street']").val(result.street);
                                    self.$('.pe_is_validate').val(true);//attr('checked', true);
                                    //self.$('.vat').val(vat);
                                    self.$('.pe_last_update').val(result.last_update);
                                    self.$("[name='pe_state']").val(result.state);
                                    self.$("[name='pe_condition']").val(result.condition);

                                    self.$("[name='city']").val(result.city);
                                    self.$("[name='state_id']").val(result.state_id);
                                    self.$("[name='l10n_pe_district']").val(result.l10n_pe_district);
                                    self.$("[name='zip']").val(result.zip);

                                    self.$("[name='city_id']").val(result.city_id);
                                    
                                    sself.changes['name'] = result.legal_name;
                                    sself.changes['pe_commercial_name'] = result.commercial_name;
                                    sself.changes['pe_legal_name'] = result.legal_name;
                                    sself.changes['street'] = result.street;
                                    sself.changes['pe_is_validate'] = true;
                                    sself.changes['pe_last_update'] = result.last_update;
                                    sself.changes['pe_state'] = result.state;
                                    sself.changes['pe_condition'] = result.condition;
                                    sself.changes['city'] = result.city;
                                    sself.changes['state_id'] = result.state_id;
                                    sself.changes['l10n_pe_district'] = result.l10n_pe_district;
                                    sself.changes['zip'] = result.zip;
                                }
                            }
                        }).catch(function (error){
                            console.log('Failed to get partner:');
                        });
                    }
                }
            }
        
        };

    Registries.Component.extend(ClientDetailsEdit, PosResClientDetailsEdit);

    return PosResClientDetailsEdit;
});
