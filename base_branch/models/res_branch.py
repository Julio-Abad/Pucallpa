# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import logging
import os

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class CompanyBranch(models.Model):
    _name = "res.company.branch"
    _description = 'Branch'
    _order = 'sequence, name'

    def copy(self, default=None):
        raise UserError(_('Duplicating a branch is not allowed. Please create a new branch instead.'))

    def _get_logo(self):
        return base64.b64encode(open(os.path.join(tools.config['root_path'], 'addons', 'base', 'static', 'img', 'res_company_logo.png'), 'rb') .read())
    
    def _default_company_id(self):
        return self.env.company.id
    
    name = fields.Char(related='partner_id.name', string='Branch Name', required=True, store=True, readonly=False)
    sequence = fields.Integer(help='Used to order Companies in the branch switcher', default=10)
    company_id = fields.Many2one('res.company', string='Company', default=_default_company_id, index=True, required=True)
    parent_id = fields.Many2one('res.partner', string='Parent Branch', related="company_id.partner_id", store=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    logo = fields.Binary(related='partner_id.image_1920', default=_get_logo, string="Branch Logo", readonly=False)
    
    user_ids = fields.Many2many('res.users', 'res_branch_users_rel', 'cid', 'user_id', string='Accepted Users')
    street = fields.Char(compute='_compute_address', inverse='_inverse_street')
    street2 = fields.Char(compute='_compute_address', inverse='_inverse_street2')
    zip = fields.Char(compute='_compute_address', inverse='_inverse_zip')
    city = fields.Char(compute='_compute_address', inverse='_inverse_city')
    state_id = fields.Many2one(
        'res.country.state', compute='_compute_address', inverse='_inverse_state',
        string="Fed. State", domain="[('country_id', '=?', country_id)]"
    )
    country_id = fields.Many2one('res.country', compute='_compute_address', inverse='_inverse_country', string="Country")
    email = fields.Char(related='partner_id.email', store=True, readonly=False)
    phone = fields.Char(related='partner_id.phone', store=True, readonly=False)
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The branch name must be unique !')
    ]

    def _get_branch_address_field_names(self):
        """ Return a list of fields coming from the address partner to match
        on branch address fields. Fields are labeled same on both models. """
        return ['street', 'street2', 'city', 'zip', 'state_id', 'country_id']

    def _get_branch_address_update(self, partner):
        return dict((fname, partner[fname])
                    for fname in self._get_branch_address_field_names())

    def _compute_address(self):
        for branch in self.filtered(lambda branch: branch.partner_id):
            address_data = branch.partner_id.sudo().address_get(adr_pref=['contact'])
            if address_data['contact']:
                partner = branch.partner_id.browse(address_data['contact']).sudo()
                branch.update(branch._get_branch_address_update(partner))

    def _inverse_street(self):
        for branch in self:
            branch.partner_id.street = branch.street

    def _inverse_street2(self):
        for branch in self:
            branch.partner_id.street2 = branch.street2

    def _inverse_zip(self):
        for branch in self:
            branch.partner_id.zip = branch.zip

    def _inverse_city(self):
        for branch in self:
            branch.partner_id.city = branch.city

    def _inverse_state(self):
        for branch in self:
            branch.partner_id.state_id = branch.state_id

    def _inverse_country(self):
        for branch in self:
            branch.partner_id.country_id = branch.country_id

    @api.onchange('state_id')
    def _onchange_state(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        context = dict(self.env.context)
        newself = self
        if context.pop('user_preference', None):
            # We browse as superuser. Otherwise, the user would be able to
            # select only the currently visible companies (according to rules,
            # which are probably to allow to see the child companies) even if
            # she belongs to some other companies.
            branches = self.env.user.branch_ids
            args = (args or []) + [('id', 'in', branches.ids)]
            newself = newself.sudo()
        return super(CompanyBranch, newself.with_context(context))._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

    @api.model
    @api.returns('self', lambda value: value.id)
    def _branch_default_get(self, object=False, field=False):
        """ Returns the user's branch
            - Deprecated
        """
        _logger.warning("The method '_branch_default_get' on res.company.branch is deprecated and shouldn't be used anymore")
        return self._get_main_branch()

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals.get('partner_id'):
            self.clear_caches()
            return super(CompanyBranch, self).create(vals)
        partner = self.env['res.partner'].create({
            'name': vals['name'],
            #'is_company': True,
            'image_1920': vals.get('logo'),
            'email': vals.get('email'),
            'phone': vals.get('phone'),
            'website': vals.get('website'),
            'vat': vals.get('vat'),
            'country_id': vals.get('country_id'),
            'parent_id': self.env['res.company'].browse(vals.get('company_id')).partner_id.id,
            'type':'other'
        })
        # compute stored fields, for example address dependent fields
        partner.flush()
        vals['partner_id'] = partner.id
        self.clear_caches()
        branch = super(CompanyBranch, self).create(vals)
        # The write is made on the user to set it automatically in the multi branch group.
        self.env.user.write({'branch_ids': [(4, branch.id)]})
        return branch

    def write(self, values):
        self.clear_caches()
        res = super(CompanyBranch, self).write(values)
        branch_address_fields = self._get_branch_address_field_names()
        branch_address_fields_upd = set(branch_address_fields) & set(values.keys())
        if branch_address_fields_upd:
            self.invalidate_cache(fnames=branch_address_fields)
        return res

    @api.model
    def _get_main_branch(self):
        try:
            main_branch = self.sudo().env.ref('base.main_company_branch')
        except ValueError:
            main_branch = self.env['res.company.branch'].sudo().search([], limit=1, order="id")
        return main_branch
