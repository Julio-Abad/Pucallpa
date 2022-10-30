# Copyright 2009 Camptocamp
# Copyright 2009 Grzegorz Grzelak
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# 2020 Tupaq 
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from collections import defaultdict
from datetime import date, timedelta
import requests

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResCurrencyRateProviderSUNAT(models.Model):
    _inherit = "res.currency.rate.provider"

    service = fields.Selection(
        selection_add=[('SUNAT', 'SUNAT')],
        ondelete={"SUNAT": "set default"},
    )

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != 'SUNAT':
            return super()._get_supported_currencies()  # pragma: no cover
        return \
            [
                'USD', 'PEN'
            ]

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        if self.service != 'SUNAT':
            return super()._obtain_rates(base_currency, currencies, date_from,
                                         date_to)  # pragma: no cover

        if base_currency not in ['PEN', 'USD']:  # pragma: no cover
            raise UserError(_(
                'SUNAT is suitable only for companies'
                ' with PEN or USD as base currency!'
            ))
        
        days = date_to - date_from
        if days.days < 0:
            raise UserError(_('The end date must be greater than the date from'))
        
        res = defaultdict(dict)
        for day in range(days.days+1):
            date = date_from + timedelta(day)
            response = requests.get('http://api.grupoyacck.com/tipocambio/sunat/%s/'%date.isoformat())
            if response.status_code == 200:
                data = response.json()
                rate = data.get('rates',[])
                if not rate:
                    continue
                if base_currency == 'PEN':
                    res[data.get('date')]['USD'] = 1/rate[0].get('sale_value')
                elif base_currency == 'USD':
                    res[data.get('date')]['PEN'] = rate[0].get('sale_value')
        return res


