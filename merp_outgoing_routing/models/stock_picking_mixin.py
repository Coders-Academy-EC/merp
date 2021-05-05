# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import models

import logging

_logger = logging.getLogger(__file__)


class StockPickingMixin(models.AbstractModel):
    _name = 'stock.picking.mixin'
    _description = 'Stock Picking Mixin'

    def _read_record(self, record_tuple):
        """
        record_tuple = (
            ('id', 100),
            ('_type', 'stock.move.line'),
        )
        id:: number (int)
        _type:: 'stock.move.line' or 'stock.package_level' (str)
        """
        record_dict = dict(record_tuple)
        record = self.env[record_dict['_type']].browse(record_dict['id'])
        record_dict.update(record.read()[0])
        return record_dict

    def serialize_record_ventor(self, rec_id):
        """Record serialization for the Ventor app."""
        filtered_list = []
        try:
            stock_object = self.search([
                ('id', '=', int(rec_id)),
            ])
        except Exception as ex:
            _logger.error(ex)
            return filtered_list

        full_list = [rec._get_operation_tuple() for rec in stock_object.operations_to_pick]
        [filtered_list.append(rec) for rec in full_list if rec not in filtered_list]
        return [self._read_record(rec) for rec in filtered_list]
