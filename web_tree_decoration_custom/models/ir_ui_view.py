# -*- coding: utf-8 -*-
# 
from odoo import api, models

class IrUiView(models.Model):

    _inherit = 'ir.ui.view'

    CUSTOM_DECORATIONS = {
        'decoration-bg-gray',
        'decoration-bg-purple',
        'decoration-bg-red',
        'decoration-bg-blue',
        'decoration-bg-white',
        'decoration-bg-brown',
        'decoration-bg-green',
        'decoration-bg-yellow',
    }

    """
    We remove the custom decorations in the 'arch_db' field constraint
    so that we dont have to patch the rng file or adapt the logic of
    the _check_xml() constraint.
    @see https://github.com/Noviat/noviat-apps/tree/14.0/web_tree_decoration_underline
    """
    @api.constrains('arch_db')
    def _check_xml(self):
        self = self.with_context(check_xml=True)
        return super()._check_xml()

    def read_combined(self, fields=None):
        res = super().read_combined(fields=fields)
        for decoration in self.CUSTOM_DECORATIONS:
            if self.env.context.get('check_xml') and decoration in res['arch']:
                res['arch'] = self._remove_custom_decoration(res['arch'], decoration)
        return res

    def _remove_custom_decoration(self, source, decoration):
        if decoration in source:
            s0, s1 = source.split(decoration, 1)
            s2 = s1.split('"', 2)[2]
            return s0 + self._remove_custom_decoration(s2, decoration)
        else:
            return source
