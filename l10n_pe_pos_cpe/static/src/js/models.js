odoo.define('l10n_pe_pos_cpe.models', function (require) {
"use strict";

var models = require('point_of_sale.models');
var core = require('web.core');
var rpc = require('web.rpc');

var _t      = core._t;

var PosModelSuper = models.PosModel;
var OrderSuper = models.Order;

models.load_fields("res.company", ["pe_max_amount"]);

models.load_models({
    model: 'account.journal',
    fields: ['name','pe_invoice_code','pe_sequence_prefix','pe_sequence_number','pe_padding', 'pe_is_cpe'],
    domain: function(self){
        if(!self.config.invoice_journal_ids){
            return [['pe_invoice_code','in',['01','03']]];      
        }
        else{
            return [['id', 'in', self.config.invoice_journal_ids]];
        }
    },
    loaded: function(self,journals){
        //self.journals = journals;
        self.db.add_pe_journals(journals);
    }
});

models.PosModel = models.PosModel.extend({
    push_and_invoice_order: function (order) {
        var self = this;
        var invoiced = new Promise(function (resolveInvoiced, rejectInvoiced) {
            if(!order.get_client()){
                rejectInvoiced({code:400, message:'Missing Customer', data:{}});
            }
            else {
                var order_id = self.db.add_order(order.export_as_JSON());

                self.flush_mutex.exec(function () {
                    var done =  new Promise(function (resolveDone, rejectDone) {
                        var transfer = self._flush_orders([self.db.get_order(order_id)], {timeout:30000, to_invoice:true});

                        transfer.catch(function (error) {
                            rejectInvoiced(error);
                            rejectDone();
                        });
                        transfer.then(function(order_server_id){
                            if (order_server_id.length) {
                                resolveInvoiced(order_server_id);
                                resolveDone();
                            } else {
                                rejectInvoiced({code:401, message:'Backend Invoice', data:{order: order}});
                                rejectDone();
                            }
                            /*if (order_server_id.length) {


                                self.rpc({
                                    model: 'pos.order',
                                    method: 'get_pe_invoice_from_ui',
                                    args: [order_server_id],
                                }, {
                                    timeout: 30000,
                                    //shadow: true,
                                })
                                .then(function (data) {
                                    order.set_pe_qr_code(data.pe_qr_code);
                                    order.set_pe_invoice_name(data.pe_invoice_name);
                                    order.set_pe_move_name(data.pe_move_name);
                                    resolveDone();
                                }).catch(function (reason){
                                    console.log('Failed to remove orders:', order_server_id);
                                });

                            } else if (order_server_id.length) {
                                resolveInvoiced(order_server_id);
                                resolveDone();
                            } else {
                                rejectInvoiced({code:401, message:'Backend Invoice', data:{order: order}});
                                rejectDone();
                            }*/
                        });
                        return done;
                    });
                });
            }
        });

        return invoiced;
    },
    check_pe_move_name: function(pe_journal_id) {
        var self = this;
        var pe_move_name = rpc.query({
            model: 'account.journal',
            method: 'get_pe_move_name',
            args: [pe_journal_id],
        }, {
            timeout: 7200,
        })
        .then(function (result) {
            if(result.pe_sequence_number>self.db.get_pe_journal_id_sequence(pe_journal_id)){
                self.db.set_pe_journal_id_sequence(pe_journal_id, result.pe_sequence_number)
            }
        }).catch(function (error){
            console.log('Failed to get sequence number');
        });
    } ,
    generate_sync_pe_move_name: function(pe_journal_id) {
        var journal_id = this.db.get_pe_journals_by_id(pe_journal_id);
        var num = "%0"+journal_id.pe_padding+"d";
        var prefix = journal_id.pe_sequence_prefix || "";
        var increment = this.db.get_pe_journal_id_sequence(pe_journal_id)+1;
        var number = prefix + num.sprintf(parseInt(increment));
        return { 'pe_move_name': number, 'pe_sequence_number':increment};
    },
    get_pe_move_name: function(pe_journal_id){
        var number = this.generate_sync_pe_move_name(pe_journal_id);
        if (this.db.get_pe_move_names().indexOf(number.pe_move_name)!=-1){
            this.db.set_pe_journal_id_sequence(pe_journal_id, number.pe_sequence_number);
            this.db.add_pe_move_names(number.pe_move_name);
            number = this.get_pe_move_name(pe_journal_id);
        }
        this.db.set_pe_journal_id_sequence(pe_journal_id, number.pe_sequence_number);
        this.db.add_pe_move_names(number.pe_move_name);
        this.check_pe_move_name(pe_journal_id);
        return number;
    }

});

models.Order = models.Order.extend({
    initialize: function(attributes,options){
        OrderSuper.prototype.initialize.apply(this, arguments);
        this.pe_qr_code = false;
        this.pe_invoice_name = false;
        this.pe_move_name = false;
        this.pe_journal_id = false;
        this.to_invoice = this.pos.config.pe_auto_journal_select;

    },
    set_pe_qr_code: function(pe_qr_code) {
        this.pe_qr_code = pe_qr_code;
    },
    set_pe_invoice_name: function(pe_invoice_name) {
        this.pe_invoice_name = pe_invoice_name;
    },
    set_pe_move_name: function(pe_move_name) {
        this.pe_move_name = pe_move_name;
    },
    get_pe_move_name: function() {
        return this.pe_move_name;
    },
    set_pe_journal_id: function(pe_journal_id) {
        var journal = this.pos.db.get_pe_journals_by_id(pe_journal_id);
        var name = '';
        if (pe_journal_id && journal){
            if (journal.pe_invoice_code == '01'){
                name+='Factura ';
            }
            if (journal.pe_invoice_code == '03'){
                name+='Boleta de venta ';
            }
            if (journal.pe_invoice_code == '07'){
                name+='Nota de crédito ';
            }
            if (journal.pe_invoice_code == '08'){
                name+='Nota de débito ';
            }
            if (journal.pe_is_cpe){
                name+='Electronica';
            }
            
        }
        this.pe_invoice_name = name;
        this.pe_journal_id = pe_journal_id;
    },
    get_pe_journal_id: function() {
        return this.pe_journal_id;
    },
    calculate_pe_document_type: function() {
        if (!this.get_client()){
            this.set_pe_journal_id(false);
            return ;
        }
        if (this.get_pe_doc_type() == '6'){
            this.set_pe_journal_id(this.pos.db.get_pe_journals_by_pe_invoice_code('01'));
        }
        else{
            this.set_pe_journal_id(this.pos.db.get_pe_journals_by_pe_invoice_code('03'));   
        }
    },
    get_cpe_type: function(){
        if (this.pe_journal_id){
            var journal = this.pos.db.get_pe_journals_by_id(this.pe_journal_id);
            return journal.pe_invoice_code; 
        }
        else{
            return '';
        }
        
    },
    get_cpe_qr: function(){
        var res=[]
        res.push(this.pos.company.vat);
        res.push(this.get_cpe_type() || ' ');
        res.push(this.get_pe_move_name() || ' ');
        res.push(this.get_total_tax() || 0.0);
        res.push(this.get_total_with_tax() || 0.0);
        res.push(moment(new Date().getTime()).format('YYYY-MM-DD'));
        res.push(this.get_pe_doc_type() || '-');
        res.push(this.get_vat() || '-');
        var qr_string=res.join('|');
        return qr_string;
    },
    export_as_JSON: function(){
        var json = OrderSuper.prototype.export_as_JSON.apply(this, arguments);
        json['pe_move_name']=this.get_pe_move_name();
        json['pe_journal_id']=this.get_pe_journal_id();
        //res['date_invoice']=moment(new Date().getTime()).format('YYYY-MM-DD') ;
        return json;
    },
});

});
