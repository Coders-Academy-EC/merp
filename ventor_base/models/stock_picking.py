from odoo import fields, models, api, _


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    confirm_source_location = fields.Boolean(
        string="Confirm source location",
        help="The dot next to the field gets yellow color means user have "
             "to confirm it. User has to scan a barcode of source location"
    )

    change_source_location = fields.Boolean(
        string="Change source location",
        help="User can change default source location to pick item from another location. "
             "Works only if 'Confirm source location' setting is active",
    )

    show_next_product = fields.Boolean(
        string="Show next product",
        help="Product field will show the next product to be picked. "
             "Use the setting during picking and delivery. "
             "It is recommended to disable the setting for the reception area",
    )

    confirm_product = fields.Boolean(
        string="Confirm product",
        help="The dot next to the field gets yellow color means user have to confirm it. "
             "User has to scan a barcode of product"
    )

    apply_default_lots = fields.Boolean(
        string="Apply default lots",
        help="If it's on, you don't need to scan lot number to confirm it. "
             "On receipts the app will create default Odoo lots and apply them to the product. "
             "On delivery zone you don't need to confirm lots and "
             "they will be taken Odoo by default"
    )

    transfer_more_items = fields.Boolean(
        string="Transfer more items",
        help="Allows moving more items than expected (for example kg of meat, etc)"
    )

    confirm_destination_location = fields.Boolean(
        string="Confirm destination location",
        help="The dot next to the field gets yellow color means user have to confirm it. "
             "User has to scan a barcode of destination location"
    )

    apply_quantity_automatically = fields.Boolean(
        string="Apply quantity automatically",
        help="Automatically validate the line after scanning a destination location. "
             "Warning: you have to insert QTY first before destination location"
    )

    change_destination_location = fields.Boolean(
        string="Change destination location",
        help="If this setting is active a user can change destination location "
             "while receiving to be placed at any available location",
    )

    autocomplete_the_item_quantity_field = fields.Boolean(
        string="Autocomplete the item quantity field",
        help="Automatically insert expected quantity. No need to enter the quantity "
             "of goods using the keyboard or using scanning"
    )

    show_print_attachment_button = fields.Boolean(
        string="Show Print attachments button",
        help="Showing the Print attachments button in the toolbar instead of "
             "keeping it in the hidden menu"
    )

    show_put_in_pack_button = fields.Boolean(
        string="Show Put in pack button",
        help="Showing the Put in pack button in the toolbar instead of "
             "keeping it in the hidden menu"
    )

    manage_packages = fields.Boolean(
        string="Manage packages",
        help="Scan source (destination) packages right after scanning source (destination) "
             "location. Use it if you move from one package to another or pick items from "
             "packages or pallets. Works only if package management settings is active on Odoo side"
    )

    manage_product_owner = fields.Boolean(
        string="Manage product owner",
        help="Allow scan product owner. You can specify product owner while moving items. "
             "Working only with 'Consignment' setting on Odoo side"
    )

    @api.model
    def create(self, vals):
        if 'code' in vals:
            vals['show_next_product'] = vals['code'] != "incoming"
            vals['change_destination_location'] = True

        return super(StockPickingType, self).create(vals)

    @api.onchange('confirm_source_location')
    def _onchange_confirm_source_location(self):
        if not self.confirm_source_location:
            self.change_source_location = False

    @api.onchange('confirm_destination_location')
    def _onchange_confirm_destination_location(self):
        if not self.confirm_destination_location:
            self.apply_quantity_automatically = False

    @api.onchange('change_source_location')
    def _onchange_change_source_location(self):
        if self.change_source_location and not self.confirm_source_location:
            return {
                'warning': {
                    'title': _("Warning"),
                    'message': _("'Change source location' is available only "
                                 "if 'Confirm source location' is enabled")
                }
            }

    @api.onchange('apply_quantity_automatically')
    def _onchange_apply_quantity_automatically(self):
        if self.apply_quantity_automatically and not self.confirm_destination_location:
            return {
                'warning': {
                    'title': _("Warning"),
                    'message': _("'Autocomplete the item quantity field' is available only "
                                 "if 'Change destination location' is enabled")
                }
            }

    def write(self, vals):
        res = super(StockPickingType, self).write(vals)

        if 'change_source_location' in vals or 'confirm_source_location' in vals:
            for stock_picking_type in self:
                if stock_picking_type.change_source_location:
                    if not stock_picking_type.confirm_source_location:
                        stock_picking_type.change_source_location = False

        if 'apply_quantity_automatically' in vals or 'confirm_destination_location' in vals:
            for stock_picking_type in self:
                if stock_picking_type.apply_quantity_automatically:
                    if not stock_picking_type.confirm_destination_location:
                        stock_picking_type.apply_quantity_automatically = False

        return res

    def get_ventor_settings(self):
        return {
            "id": self.id,
            "name": self.name,
            "wh_code": self.warehouse_id.code,
            "wh_name": self.warehouse_id.name,
            "settings": {
                "confirm_source_location": self.confirm_source_location,
                "change_source_location": self.change_source_location,
                "show_next_product": self.show_next_product,
                "confirm_product": self.confirm_product,
                "apply_default_lots": self.apply_default_lots,
                "transfer_more_items": self.transfer_more_items,
                "confirm_destination_location": self.confirm_destination_location,
                "apply_quantity_automatically": self.apply_quantity_automatically,
                "change_destination_location": self.change_destination_location,
                "autocomplete_the_item_quantity_field": self.autocomplete_the_item_quantity_field,
                "show_print_attachment_button": self.show_print_attachment_button,
                "show_put_in_pack_button": self.show_put_in_pack_button,
                "manage_packages": self.manage_packages,
                "manage_product_owner": self.manage_product_owner,
            }
        }
