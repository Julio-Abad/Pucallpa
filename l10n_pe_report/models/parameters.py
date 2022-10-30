# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, exceptions

class FleetVehicleChofer(models.Model):
    _name = "fleet.vehicle.chofer"
    _description = 'Chofer'

    name = fields.Char(string='Nombre', oldname='x_name')
    licencia = fields.Char(string='Licencia', oldname='x_studio_licencia')
    categoria = fields.Char(string='Categoría', oldname='x_studio_categoria')
    nro_dni = fields.Char(string='DNI', oldname='x_studio_dni')

class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    registro_mtc = fields.Char('Numero de Guia', oldname='x_studio_registro_mtc')

###################################################################################
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    proyect = fields.Char(string='Proyecto')

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res.update({"proyect": self.proyect})
        #print(res)
        return res


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    proyect = fields.Char(string='Proyecto')

class ResCompany(models.Model):
    _inherit = "res.company"

    account_bank = fields.Binary(string="Cuentas de Bancos")

#################################################################################
class StockPickingMotive(models.Model):
    _name = 'stock.picking.motive'
    _description = "Motivos"
    
    active = fields.Boolean('Activo?', default=True)
    sequence = fields.Integer('sequence', help="Sequence for the handle.", default=0)
    name = fields.Char('Nombre', required=True)

class PickingType(models.Model):
    _inherit = "stock.picking"

    pe_number = fields.Char('Numero de Guia')
    einvoice_12 = fields.Many2one('einvoice.catalog.12', u'Tipo de Operacion SUNAT')
    invoice_id = fields.Many2one('account.move', 'Factura')
    fecha_kardex = fields.Date(string='Fecha kardex', readonly=False)
    state_invoice = fields.Char(u'Estado de factura')
    es_fecha_kardex = fields.Boolean('Usar Fecha kardex', default=True)
    po_id = fields.Many2one('stock.picking', 'Orden de pedido')

    #propietario_id = fields.Many2one('res.partner', 'Propietario')
    vehiculo_id = fields.Many2one('fleet.vehicle', 'Vehiculo')
    marca_id = fields.Many2one(related="vehiculo_id.model_id.brand_id", string='Marca', size=12)
    placa = fields.Char(related="vehiculo_id.license_plate", string='Placa', size=12)
    certificado_mtc = fields.Char(related="vehiculo_id.registro_mtc",string="Certificado M.T.C.")
    
    chofer_id = fields.Many2one('fleet.vehicle.chofer', string='Chofer')
    licencia = fields.Char(related="chofer_id.licencia", string='Licencia de Conducir N°(5)', size=12)
    nombre = fields.Char(related="chofer_id.name", string='Nombre')
    ruc = fields.Char(related="chofer_id.nro_dni", string='RUC', size=100)

    customer_id = fields.Many2one("res.partner", string="Cliente")
    salesman_id = fields.Many2one("res.users", string="Vendedor")
    motive_id = fields.Many2one("stock.picking.motive", string="Motivo de Reclamo")
    suma_peso_total = fields.Float(compute='_compute_suma_total', string="Peso Total")
    nro_const = fields.Char('Numero de constancia de inscripcion', size=12)

    tipo = fields.Char('Tipo', size=12)
    nro_comp = fields.Char('Numero de comprobante', size=12)
    nro_guia = fields.Char('Numero de guia', size=12)
    fecha_traslado = fields.Datetime(string='Fecha de traslado')
    comprobante = fields.Char(string='Comprobante')
    punto_partida = fields.Char('Punto de partida', size=100)
    punto_llegada = fields.Char('Punto de llegada', size=100)

    @api.depends('move_ids_without_package.peso_total')
    def _compute_suma_total(self):
        for record in self:
            record.suma_peso_total = sum(line.peso_total for line in record.move_ids_without_package)

    @api.model
    def create(self, vals):
        t = super(PickingType, self).create(vals)
        if t.picking_type_id.warehouse_id.id and t.picking_type_id.warehouse_id.partner_id.id and t.picking_type_id.warehouse_id.partner_id.street:
            t.punto_partida = t.picking_type_id.warehouse_id.partner_id.street
        if t.partner_id.id:
            t.punto_llegada = t.partner_id.street
        return t

    def write(self, vals):
        # if 'partner_id' in vals:
        # 	if vals['partner_id']:
        # 		p = self.env['res.partner'].browse(vals['partner_id'])
        # 		vals['punto_llegada'] = p.street if p.street else False
        # 	else:
        # 		vals['punto_llegada'] = False

        if 'picking_type_id' in vals:
            p = self.env['stock.picking.type'].browse(vals['picking_type_id'])
            if p.warehouse_id.id and p.warehouse_id.partner_id.id:
                vals['punto_partida'] = p.warehouse_id.partner_id.street if p.warehouse_id.partner_id.street else False

        t = super(PickingType, self).write(vals)
        return t

    def _create_backorder(self, backorder_moves=[]):
        """ Move all non-done lines into a new backorder picking. If the key 'do_only_split' is given in the context, then move all lines not in context.get('split', []) instead of all non-done lines.
        """
        # TDE note: o2o conversion, todo multi
        backorders = super(PickingType, self)._create_backorder()
        #for backorder in backorders:
        #    for i in backorder.pack_operation_product_ids:
        #        p_qty = i.product_qty
        #        i.write({'qty_done': p_qty})
        return backorders

class StockMove(models.Model):
    _inherit = "stock.move"

    peso_total = fields.Float(compute='_compute_peso_total', string="Peso Total")

    @api.depends('peso_total')
    def _compute_peso_total(self):
        self.mapped(lambda record: record.update({
            'peso_total': record.quantity_done * record.product_id.weight
        }))
