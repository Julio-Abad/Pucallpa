odoo.define('l10n_pe_pos.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var PosDB =require('point_of_sale.DB');
    var core    = require('web.core');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;

    var utils = require('web.utils');
    var round_pr = utils.round_precision;

    var _t      = core._t;

    var OrderSuper = models.Order;
    var OrderOrderline = models.Orderline;

    models.load_fields("account.tax", ["pe_tax_code", "description"]);


    models.Order = models.Order.extend({
        pe_get_tax_details: function(){
            var details = {};
            var basedetails = {};
            var fulldetails = [];

            var subtotal = 0.0;

            var self = this;

            this.orderlines.each(function(line){
                var taxes = line.pe_get_tax_details();
                var ldetails = taxes.taxDetails;
                var lbasedetails = taxes.taxBaseDetails;
                for(var id in ldetails){
                    if(ldetails.hasOwnProperty(id)){
                        details[id] = (details[id] || 0) + ldetails[id];
                    }
                }
                for(var id in lbasedetails){
                    if(lbasedetails.hasOwnProperty(id)){
                        basedetails[id] = (basedetails[id] || 0) + lbasedetails[id];
                        if (self.pos.taxes_by_id[id].pe_tax_code == '1000'){
                            subtotal = subtotal + lbasedetails[id];
                        }
                    }
                }
            });

            fulldetails.push({amount:subtotal, tax: {}, name: "Subtotal"});

            for(var id in basedetails){
                if(basedetails.hasOwnProperty(id)){
                    if (!['1000', '7152'].includes(this.pos.taxes_by_id[id].pe_tax_code)){
                        fulldetails.push({amount: basedetails[id], tax: this.pos.taxes_by_id[id], name: this.pos.taxes_by_id[id].description});
                    }
                        
                }
            }

            for(var id in details){
                if(details.hasOwnProperty(id)){
                    if(details[id]>0.0){
                        fulldetails.push({amount: details[id], tax: this.pos.taxes_by_id[id], name: this.pos.taxes_by_id[id].name});    
                    }
                }
            }

            return fulldetails;
        },

    });

    models.Orderline = models.Orderline.extend({
        pe_get_tax_details: function(){
            var prices = this.pe_get_all_prices()
            return {'taxDetails': prices.taxDetails, 'taxBaseDetails':prices.taxBaseDetails};
        },
        pe_compute_all: function(taxes, price_unit, quantity, currency_rounding, no_map_tax) {
            var self = this;
            var list_taxes = [];
            var currency_rounding_bak = currency_rounding;
            if (this.pos.company.tax_calculation_rounding_method == "round_globally"){
               currency_rounding = currency_rounding * 0.00001;
            }
            var total_excluded = round_pr(price_unit * quantity, currency_rounding);
            var total_included = total_excluded;
            var base = total_excluded;

            _(taxes).each(function(tax) {
                if (!no_map_tax){
                    tax = self._map_tax_fiscal_position(tax);
                }
                if (!tax){
                    return;
                }
                if (tax.amount_type === 'group'){
                    var ret = self.compute_all(tax.children_tax_ids, price_unit, quantity, currency_rounding);
                    total_excluded = ret.total_excluded;
                    base = ret.total_excluded;
                    total_included = ret.total_included;
                    list_taxes = list_taxes.concat(ret.taxes);
                }
                else {
                    var tax_amount = self._compute_all(tax, base, quantity);
                    tax_amount = round_pr(tax_amount, currency_rounding);

                    if (tax.price_include) {
                        total_excluded -= tax_amount;
                        base -= tax_amount;
                    }
                    else {
                        total_included += tax_amount;
                    }
                    /*if (tax.include_base_amount) {
                        base += tax_amount;
                    }*/
                    var data = {
                        id: tax.id,
                        base: base,
                        amount: tax_amount,
                        name: tax.name,
                    };
                    list_taxes.push(data);
                    
                }
            });
            return {
                taxes: list_taxes,
                total_excluded: round_pr(total_excluded, currency_rounding_bak),
                total_included: round_pr(total_included, currency_rounding_bak)
            };
        },
        pe_get_all_prices: function(){
            var price_unit = this.get_unit_price() * (1.0 - (this.get_discount() / 100.0));
            var taxtotal = 0;

            var product =  this.get_product();
            var taxes_ids = product.taxes_id;
            var taxes =  this.pos.taxes;
            var taxdetail = {};
            var taxbasedetail = {};
            var product_taxes = [];

            _(taxes_ids).each(function(el){
                product_taxes.push(_.detect(taxes, function(t){
                    return t.id === el;
                }));
            });

            var all_taxes = this.pe_compute_all(product_taxes, price_unit, this.get_quantity(), this.pos.currency.rounding);
            _(all_taxes.taxes).each(function(tax) {
                taxtotal += tax.amount;
                taxdetail[tax.id] = tax.amount;
                taxbasedetail[tax.id] = tax.base;
            });

            return {
                "priceWithTax": all_taxes.total_included,
                "priceWithoutTax": all_taxes.total_excluded,
                "tax": taxtotal,
                "taxDetails": taxdetail,
                "taxBaseDetails": taxbasedetail,
            };
        },

    });

});