# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class ShopinvaderImageMixin(models.AbstractModel):
    _inherit = 'shopinvader.image.mixin'

    @api.multi
    def _prepare_data_resize(self, thumbnail):
        """
        Inherit to replace the url ("src" key of dict)
        :param thumbnail: storage.thumbnail recordset
        :return: dict
        """
        self.ensure_one()
        values = super(ShopinvaderImageMixin, self)._prepare_data_resize(
            thumbnail=thumbnail)
        url_key = "src"
        url = values.get(url_key)
        if url and 'backend_id' in self._fields:
            new_url = self.backend_id._replace_by_proxy(url)
            if url != new_url:
                values.update({
                    url_key: new_url,
                })
        return values
