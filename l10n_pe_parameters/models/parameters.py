# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    account_bank = fields.Binary(string="Cuentas de Bancos")
    type_report = fields.Selection([('horizontal', 'Horizontal'), ('vertical', 'Vertical')],
                                   String="Formato impreso", index=True, default='horizontal')


class FleetVehicleChofer(models.Model):
    _name = "fleet.vehicle.chofer"
    _description = 'Chofer'

    name = fields.Char(string='Nombre', oldname='x_name')
    licencia = fields.Char(string='Licencia', oldname='x_studio_licencia')
    categoria = fields.Char(string='Categoría', oldname='x_studio_categoria')
    nro_dni = fields.Char(string='DNI', oldname='x_studio_dni')


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    registro_mtc = fields.Char(
        'Certificado M.T.C.', oldname='x_studio_registro_mtc')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    proyect = fields.Char(string='Proyecto')

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res.update({"proyect": self.proyect})
        return res


class AccountMove(models.Model):
    _inherit = 'account.move'

    proyect = fields.Char(string='Proyecto')
    l10n_pe_currency_rate = fields.Float(
        string="Tipo de cambio",
        compute="_compute_l10n_pe_currency_rate",
        digits=(12, 3),
        store=True
    )
    hide_currency_rate = fields.Boolean(compute="_compute_hide_currency_rate")

    # OBTENER TC PARA LA FECHA DE LA FACTURA
    @api.depends('invoice_date', 'currency_id')
    def _compute_l10n_pe_currency_rate(self):
        for record in self:
            rate = 1
            if record.company_id.currency_id != record.currency_id:
                currency_rate = self.env['res.currency.rate'].search([
                    ('currency_id', '=', record.currency_id.id),
                    ('name', '=', record.invoice_date)
                ], limit=1)
                if currency_rate:
                    rate = round(1.000 / currency_rate.rate, 3)
            record.l10n_pe_currency_rate = rate

    @api.depends('currency_id')
    def _compute_hide_currency_rate(self):
        for record in self:
            result = True
            if record.company_id.currency_id != record.currency_id:
                result = False
            record.hide_currency_rate = result

    def _get_invoice_date_currency_rate(self):
        for record in self:
            rate = "{0:.3f}".format(record.l10n_pe_currency_rate)
            pre = post = u''
            display_currency = record.company_id.currency_id
            if display_currency.position == 'before':
                pre = u'{symbol}\N{NO-BREAK SPACE}'.format(symbol=display_currency.symbol or '')
            else:
                post = u'\N{NO-BREAK SPACE}{symbol}'.format(symbol=display_currency.symbol or '')

            return u'{pre}{0}{post}'.format(rate, pre=pre, post=post)

    def action_post(self):
        for record in self:
            if record.company_id.currency_id != record.currency_id:
                record._compute_l10n_pe_currency_rate()
        return super(AccountMove, self).action_post()

    def action_invoice_print(self):
        super(AccountMove, self).action_invoice_print()
        return self.env.ref('l10n_pe_parameters.cpe_move_reports').report_action(self)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context.get('picking_invoice') and self._context.get('picking_id'):
            picking_id = self.env['stock.picking'].browse([self._context.get('picking_id')])
            invoice_ids = []
            if picking_id.sale_id:
                invoice_ids = picking_id.sale_id.invoice_ids.ids
            if picking_id.purchase_id:
                invoice_ids = picking_id.purchase_id.invoice_ids.ids
            return self.search([('id', 'in', invoice_ids)]).name_get()
        return super(AccountMove, self).name_search(name, args=args, operator=operator, limit=limit)


class StockPickingMotive(models.Model):
    _name = 'stock.picking.motive'
    _description = "Motivos"

    active = fields.Boolean('Activo?', default=True)
    sequence = fields.Integer(
        'sequence', help="Sequence for the handle.", default=0)
    name = fields.Char('Nombre', required=True)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    pe_number = fields.Char(related='pe_guide_number',
                            string='Numero de Guia', store=True)
    einvoice_12 = fields.Many2one(
        'einvoice.catalog.12', u'Tipo de Operacion SUNAT')
    invoice_id = fields.Many2one('account.move', 'Factura')
    fecha_kardex = fields.Date(string='Fecha kardex', readonly=False)
    state_invoice = fields.Char(u'Estado de factura')
    es_fecha_kardex = fields.Boolean('Usar Fecha kardex', default=True)
    po_id = fields.Many2one('stock.picking', 'Orden de pedido')

    vehiculo_id = fields.Many2one('fleet.vehicle', 'Vehiculo')
    marca_id = fields.Many2one(
        related="vehiculo_id.model_id.brand_id", string='Marca', size=12, store=True)
    placa = fields.Char(related="vehiculo_id.license_plate",
                        string='Placa', size=12, store=True)
    certificado_mtc = fields.Char(
        related="vehiculo_id.registro_mtc", string="Certificado M.T.C.", store=True)

    chofer_id = fields.Many2one('fleet.vehicle.chofer', string='Chofer')
    licencia = fields.Char(related="chofer_id.licencia",
                           string='Licencia de Conducir N°(5)', size=12, store=True)
    nombre = fields.Char(related="chofer_id.name", string='Nombre', store=True)
    ruc = fields.Char(related="chofer_id.nro_dni",
                      string='RUC', size=100, store=True)

    customer_id = fields.Many2one("res.partner", string="Cliente")
    salesman_id = fields.Many2one("res.users", string="Vendedor")
    motive_id = fields.Many2one(
        "stock.picking.motive", string="Motivo de Reclamo")
    suma_peso_total = fields.Float(
        compute='_compute_suma_total', string="Peso Total")
    nro_const = fields.Char('Numero de constancia de inscripcion', size=12)

    tipo = fields.Char('Tipo', size=12)
    nro_comp = fields.Char('Numero de comprobante', size=12)
    nro_guia = fields.Char('Numero de guia', size=12)
    fecha_traslado = fields.Datetime(string='Fecha de traslado')
    comprobante = fields.Char(string='Comprobante')
    punto_partida = fields.Char('Punto de partida', size=100)
    punto_llegada = fields.Char('Punto de llegada', size=100)

    payment_term_id = fields.Many2one(
        "account.payment.term", string="Plazos de pago")

    @api.depends('move_ids_without_package.peso_total')
    def _compute_suma_total(self):
        for record in self:
            record.suma_peso_total = sum(
                line.peso_total for line in record.move_ids_without_package)
            record.pe_gross_weight = record.suma_peso_total

            record.pe_unit_quantity = sum(
                line.quantity_done for line in record.move_ids_without_package)

    @api.model
    def create(self, vals):
        t = super(StockPicking, self).create(vals)
        if t.picking_type_id.warehouse_id.id and t.picking_type_id.warehouse_id.partner_id.id and t.picking_type_id.warehouse_id.partner_id.street:
            t.punto_partida = t.picking_type_id.warehouse_id.partner_id.street
        if t.partner_id.id:
            t.punto_llegada = t.partner_id.street
        return t

    def write(self, vals):
        if 'picking_type_id' in vals:
            p = self.env['stock.picking.type'].browse(vals['picking_type_id'])
            if p.warehouse_id.id and p.warehouse_id.partner_id.id:
                vals['punto_partida'] = p.warehouse_id.partner_id.street if p.warehouse_id.partner_id.street else False
        t = super(StockPicking, self).write(vals)
        return t

    def _create_backorder(self, backorder_moves=[]):
        """ Move all non-done lines into a new backorder picking. If the key 'do_only_split' is given in the context, then move all lines not in context.get('split', []) instead of all non-done lines.
        """
        # TDE note: o2o conversion, todo multi
        backorders = super(StockPicking, self)._create_backorder()
        return backorders


class StockMove(models.Model):
    _inherit = "stock.move"

    peso_total = fields.Float(
        compute='_compute_peso_total', string="Peso Total")

    @api.depends('peso_total')
    def _compute_peso_total(self):
        self.mapped(lambda record: record.update({
            'peso_total': record.quantity_done * record.product_id.weight
        }))
