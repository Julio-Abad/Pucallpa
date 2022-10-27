odoo.define('l10n_pe_pos.models', function (require) {
"use strict";

var models = require('point_of_sale.models');
var core = require('web.core');
var rpc = require('web.rpc');

var _t      = core._t;

var PosModelSuper = models.PosModel;
var OrderSuper = models.Order;

models.load_fields("res.company", ["l10n_pe_district","city_id","state_id", "zip", "street"]);
models.load_fields("res.currency", ["currency_unit_label", "currency_subunit_label"]);
models.load_fields("res.partner", ["pe_doc_type", "pe_commercial_name", "pe_legal_name", "pe_is_validate", "pe_state", "pe_condition"]);

models.load_fields("account.tax", ["description","l10n_pe_edi_tax_code"]);


models.PosModel = models.PosModel.extend({
    initialize: function(session, attributes) {
        var res = PosModelSuper.prototype.initialize.apply(this, arguments);
        this.pe_doc_types = [
                    {'code': '0', 'name':'DOC.TRIB.NO.DOM.SIN.RUC'},
                    {'code': '1', 'name':'DNI'},
                    {'code': '4', 'name':'CARNET DE EXTRANJERIA'},
                    {'code': '6', 'name':'RUC'},
                    {'code': '7', 'name':'PASAPORTE'},
                    {'code': 'A', 'name':'CÉDULA DIPLOMÁTICA DE IDENTIDAD'}];
        this.pe_states = [
                    {'code': 'ACTIVO', 'name':'ACTIVO'},
                    {'code': 'BAJA DE OFICIO', 'name':'BAJA DE OFICIO'},
                    {'code': 'BAJA PROVISIONAL', 'name':'BAJA PROVISIONAL'},
                    {'code': 'SUSPENSION TEMPORAL', 'name':'SUSPENSION TEMPORAL'},
                    {'code': 'INHABILITADO-VENT.UN', 'name':'INHABILITADO-VENT.UN'},
                    {'code': 'BAJA MULT.INSCR. Y O', 'name':'BAJA MULT.INSCR. Y O'},
                    {'code': 'PENDIENTE DE INI. DE', 'name':'PENDIENTE DE INI. DE'},
                    {'code': 'OTROS OBLIGADOS', 'name':'OTROS OBLIGADOS'},
                    {'code': 'NUM. INTERNO IDENTIF', 'name':'NUM. INTERNO IDENTIF'},
                    {'code': 'ANUL.PROVI.-ACTO ILI', 'name':'ANUL.PROVI.-ACTO ILI'},
                    {'code': 'ANULACION - ACTO ILI', 'name':'ANULACION - ACTO ILI'},
                    {'code': 'BAJA PROV. POR OFICI', 'name':'BAJA PROV. POR OFICI'},
                    {'code': 'ANULACION - ERROR SU', 'name':'ANULACION - ERROR SU'},
                    ];
        this.pe_conditions = [
                    {'code': 'HABIDO', 'name':'HABIDO'},
                    {'code': 'NO HALLADO', 'name':'NO HALLADO'},
                    {'code': 'NO HABIDO', 'name':'NO HABIDO'},
                    {'code': 'PENDIENTE', 'name':'PENDIENTE'},
                    {'code': 'NO HALLADO SE MUDO D', 'name':'NO HALLADO SE MUDO D'},
                    {'code': 'NO HALLADO NO EXISTE', 'name':'NO HALLADO NO EXISTE'},
                    {'code': 'NO HALLADO FALLECIO', 'name':'NO HALLADO FALLECIO'},
                    {'code': 'NO HALLADO OTROS MOT', 'name':'NO HALLADO OTROS MOT'},
                    {'code': 'NO APLICABLE', 'name':'NO APLICABLE'},
                    {'code': 'NO HALLADO NRO.PUERT', 'name':'NO HALLADO NRO.PUERT'},
                    {'code': 'NO HALLADO CERRADO', 'name':'NO HALLADO CERRADO'},
                    {'code': 'POR VERIFICAR', 'name':'POR VERIFICAR'},
                    {'code': 'NO HALLADO DESTINATA', 'name':'NO HALLADO DESTINATA'},
                    {'code': 'NO HALLADO RECHAZADO', 'name':'NO HALLADO RECHAZADO'},
                    {'code': '-', 'name':'NO HABIDO'},
                    ];
        return res;
    },
    validate_pe_doc: function (pe_doc_type, vat) {
        if (!pe_doc_type || !vat){
            return true;
        }
        var regex=/^[a-zA-Z0-9]+$/;
        if(!vat.match(regex)){
            return false;
        }
        if (pe_doc_type=='1') {
            regex=/^[0-9]{8}$/;
            if(vat.match(regex)){
                return true;
            }
            else{
                return false;
            }
            
        }
        else if (pe_doc_type=='6')
        {
            regex=/^[0-9]{11}$/;
            if(!vat.match(regex)){
                return false;
            }
            var vat= vat;
            var factor = '5432765432';
            var sum = 0;
            var dig_check = false;
                    
            for (var i = 0; i < factor.length; i++) {
                sum += parseInt(factor[i]) * parseInt(vat[i]);
             } 

            var subtraction = 11 - (sum % 11);
            if (subtraction == 10){
                dig_check = 0;
            }
            else if (subtraction == 11){
                dig_check = 1;
            }
            else{
                dig_check = subtraction;
            }
            
            if (parseInt(vat[10]) != dig_check){
                return false;
            }
            return true;
        }
        else {
            return true;
        }
    },
});

models.Order = models.Order.extend({
    initialize: function(attributes,options){
        OrderSuper.prototype.initialize.apply(this, arguments);
    },
    get_pe_doc_type: function() {
        var client = this.get_client();
        var pe_doc_type=client ? client.pe_doc_type : "";
        return pe_doc_type;
    },
    get_vat: function() {
        var client = this.get_client();
        var vat=client ? client.vat : "";
        return vat;
    },
    get_amount_text: function() {
        return numeroALetras(this.get_total_with_tax(), {
                                          plural: this.pos.currency.currency_unit_label,
                                          singular: this.pos.currency.currency_unit_label,
                                          centPlural: "",
                                          centSingular: ""
                                        })
    },
    pe_get_tax_details: function() {
        var basedetails = {};
        var taxdetails = {};

        var fullDetails = [];
        var subtotal = 0.0;

        var self = this;

        var taxbycode = {}

        this.orderlines.each(function(line){
            var taxes = line.pe_get_tax_details();
            if (taxes.length>0){
                for (var i = 0; i < taxes.length; i++) {
                    var tax = self.pos.taxes_by_id[taxes[i].id];
                    if(!basedetails.hasOwnProperty(tax.l10n_pe_edi_tax_code)){
                        basedetails[tax.l10n_pe_edi_tax_code] = 0.0;
                        taxdetails[tax.l10n_pe_edi_tax_code] = 0.0;
                        taxbycode[tax.l10n_pe_edi_tax_code] = tax;
                    }
                    basedetails[tax.l10n_pe_edi_tax_code] += taxes[i].base;
                    if (taxes[i].amount>0.0){
                        taxdetails[tax.l10n_pe_edi_tax_code] += taxes[i].amount;    
                    }
                }
            }
            
        });

        for(var code in basedetails) {
            var details = {};
            details['amount'] = basedetails[code];
            details['tax'] = taxbycode[code];
            if (code == '1000'){
                details['name'] = _t('GRAVADA');
            }
            else {
                details['name'] = taxbycode[code].description;
            }
            fullDetails.push(details);
        }
        for (var code in taxdetails) {
            var details = {};
            details['amount'] = taxdetails[code];
            details['tax'] = taxbycode[code];
            details['name'] = taxbycode[code].description;
            fullDetails.push(details);
        }
        return fullDetails;
    },
});


models.Orderline = models.Orderline.extend({
    pe_get_tax_details: function(){
        var prices = this.pe_get_all_prices()
        return prices.taxes;
    },
    pe_get_all_prices: function(){
        var self = this;

        var price_unit = this.get_unit_price() * (1.0 - (this.get_discount() / 100.0));
        var taxtotal = 0;

        var product =  this.get_product();
        var taxes_ids = product.taxes_id;
        var taxes =  this.pos.taxes;
        var taxdetail = {};
        var product_taxes = [];

        _(taxes_ids).each(function(el){
            var tax = _.detect(taxes, function(t){
                return t.id === el;
            });
            product_taxes.push.apply(product_taxes, self._map_tax_fiscal_position(tax));
        });
        product_taxes = _.uniq(product_taxes, function(tax) { return tax.id; });

        var all_taxes = this.compute_all(product_taxes, price_unit, this.get_quantity(), this.pos.currency.rounding);
        return all_taxes;
    },
});

});
