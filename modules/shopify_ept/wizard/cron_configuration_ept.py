# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import UserError

_intervalTypes = {
    'days': lambda interval: relativedelta(days=interval),
    'hours': lambda interval: relativedelta(hours=interval),
    'weeks': lambda interval: relativedelta(days=7 * interval),
    'months': lambda interval: relativedelta(months=interval),
    'minutes': lambda interval: relativedelta(minutes=interval),
}


class ShopifyCronConfigurationEpt(models.TransientModel):
    """
    Common model for manage cron configuration
    """
    _name = "shopify.cron.configuration.ept"
    _description = "Shopify Cron Configuration"

    def _get_shopify_instance(self):
        return self.env.context.get('shopify_instance_id', False)

    shopify_instance_id = fields.Many2one('shopify.instance.ept', 'Shopify Instance',
                                          help="Select Shopify Instance that you want to configure.",
                                          default=_get_shopify_instance, readonly=True)

    # Auto cron for Export stock
    shopify_stock_auto_export = fields.Boolean('Export Stock', default=False,
                                               help="Check if you want to automatically Export Stock levels from Odoo"
                                                    " to Shopify.")
    shopify_inventory_export_interval_number = fields.Integer('Interval Number for Export stock',
                                                              help="Repeat every x.")
    shopify_inventory_export_interval_type = fields.Selection([('minutes', 'Minutes'), ('hours', 'Hours'),
                                                               ('days', 'Days'), ('weeks', 'Weeks'),
                                                               ('months', 'Months')], 'Interval Unit for Export Stock')
    shopify_inventory_export_next_execution = fields.Datetime('Next Execution for Export Stock ',
                                                              help='Next Execution for Export Stock')
    shopify_inventory_export_user_id = fields.Many2one('res.users', string="User for Export Inventory",
                                                       help='User for Export Inventory',
                                                       default=lambda self: self.env.user)

    # Auto cron for Import Order
    shopify_order_auto_import = fields.Boolean('Import Order', default=False,
                                               help="Check if you want to automatically Import Orders from Shopify to"
                                                    " Odoo.")
    shopify_import_order_interval_number = fields.Integer('Interval Number for Import Order', help="Repeat every x.")
    shopify_import_order_interval_type = fields.Selection([('minutes', 'Minutes'), ('hours', 'Hours'),
                                                           ('days', 'Days'), ('weeks', 'Weeks'),
                                                           ('months', 'Months')], 'Interval Unit for Import Order')
    shopify_import_order_next_execution = fields.Datetime('Next Execution for Import Order',
                                                          help='Next Execution for Import Order')
    shopify_import_order_user_id = fields.Many2one('res.users', string="User for Import Order",
                                                   help='User for Import Order',
                                                   default=lambda self: self.env.user)

    # Auto cron for Update Order Shipping Status
    shopify_order_status_auto_update = fields.Boolean('Update Order Shipping Status', default=False,
                                                      help="Check if you want to automatically Update Order Status from"
                                                           " Shopify to Odoo.")
    shopify_order_status_interval_number = fields.Integer('Interval Number for Update Order Status',
                                                          help="Repeat every x.")
    shopify_order_status_interval_type = fields.Selection([('minutes', 'Minutes'), ('hours', 'Hours'),
                                                           ('days', 'Days'), ('weeks', 'Weeks'),
                                                           ('months', 'Months')],
                                                          'Interval Unit for Update Order Status')
    shopify_order_status_next_execution = fields.Datetime('Next Execution for Update Order Status',
                                                          help='Next Execution for Update Order Status')
    shopify_order_status_user_id = fields.Many2one('res.users', string="User for Update Order Status",
                                                   help='User for Update Order Status',
                                                   default=lambda self: self.env.user)
    # Auto Import Payout Report
    shopify_auto_import_payout_report = fields.Boolean(string="Auto Import Payout Reports?")
    shopify_payout_import_interval_number = fields.Integer('Payout Import Interval Number', default=1,
                                                           help="Repeat every x.")
    shopify_payout_import_interval_type = fields.Selection([('minutes', 'Minutes'), ('hours', 'Hours'),
                                                            ('days', 'Days'), ('weeks', 'Weeks'),
                                                            ('months', 'Months')], 'Payout Import Interval Unit')
    shopify_payout_import_next_execution = fields.Datetime('Payout Import Next Execution', help='Next execution time')
    shopify_payout_import_user_id = fields.Many2one('res.users', string="Payout Import User", help='User',
                                                    default=lambda self: self.env.user)

    # Auto Process Bank Statement
    shopify_auto_process_bank_statement = fields.Boolean(string="Auto Process Bank Statement?")
    shopify_auto_process_bank_statement_interval_number = fields.Integer('Process Bank Statement Interval Number',
                                                                         default=1,
                                                                         help="Repeat every x.")
    shopify_auto_process_bank_statement_interval_type = fields.Selection([('minutes', 'Minutes'), ('hours', 'Hours'),
                                                                          ('days', 'Days'), ('weeks', 'Weeks'),
                                                                          ('months', 'Months')],
                                                                         'Process Bank Statement Interval Unit')
    shopify_auto_process_bank_statement_next_execution = fields.Datetime('Auto Process Bank Statement Next Execution',
                                                                         help='Next execution time')
    shopify_auto_process_bank_statement_user_id = fields.Many2one('res.users', string="Process Bank Statement User",
                                                                  help='User',
                                                                  default=lambda self: self.env.user)

    @api.onchange("shopify_instance_id")
    def onchange_shopify_instance_id(self):
        """
        Set field value while open the wizard
        @author: Angel Patel @Emipro Technologies Pvt. Ltd on date 16/11/2019.
        Task Id : 157716
        """
        instance = self.shopify_instance_id
        self.update_export_stock_cron_field(instance)
        self.update_import_order_cron_field(instance)
        self.update_order_status_cron_field(instance)
        self.update_payout_report_cron_field(instance)

    def update_export_stock_cron_field(self, instance):
        """
        Update and set the 'Export Inventory Stock' cron field while open the wizard
        :param instance:
        :return:
        @author: Angel Patel @Emipro Technologies Pvt. Ltd on date 16/11/2019.
        Task Id : 157716
        """
        try:
            export_inventory_stock_cron_exist = instance and self.env.ref(
                'shopify_ept.ir_cron_shopify_auto_export_inventory_instance_%d' % instance.id)
        except:
            export_inventory_stock_cron_exist = False
        if export_inventory_stock_cron_exist:
            self.shopify_stock_auto_export = export_inventory_stock_cron_exist.active or False
            self.shopify_inventory_export_interval_number = export_inventory_stock_cron_exist.interval_number or False
            self.shopify_inventory_export_interval_type = export_inventory_stock_cron_exist.interval_type or False
            self.shopify_inventory_export_next_execution = export_inventory_stock_cron_exist.nextcall or False
            self.shopify_inventory_export_user_id = export_inventory_stock_cron_exist.user_id.id or False

    def update_import_order_cron_field(self, instance):
        """
        Update and set the 'Import Sale Orders' cron field while open the wizard
        :param instance:
        :return:
        @author: Angel Patel @Emipro Technologies Pvt. Ltd on date 16/11/2019.
        Task Id : 157716
        """
        try:
            import_order_cron_exist = instance and self.env.ref(
                'shopify_ept.ir_cron_shopify_auto_import_order_instance_%d' % instance.id)
        except:
            import_order_cron_exist = False
        if import_order_cron_exist:
            self.shopify_order_auto_import = import_order_cron_exist.active or False
            self.shopify_import_order_interval_number = import_order_cron_exist.interval_number or False
            self.shopify_import_order_interval_type = import_order_cron_exist.interval_type or False
            self.shopify_import_order_next_execution = import_order_cron_exist.nextcall or False
            self.shopify_import_order_user_id = import_order_cron_exist.user_id.id or False

    def update_order_status_cron_field(self, instance):
        """
        Update and set the 'Update Order Status' cron field while open the wizard
        :param instance:
        :return:
        @author: Angel Patel @Emipro Technologies Pvt. Ltd on date 16/11/2019.
        Task Id : 157716
        """
        try:
            update_order_status_cron_exist = instance and self.env.ref(
                'shopify_ept.ir_cron_shopify_auto_update_order_status_instance_%d' % instance.id)
        except:
            update_order_status_cron_exist = False
        if update_order_status_cron_exist:
            self.shopify_order_status_auto_update = update_order_status_cron_exist.active or False
            self.shopify_order_status_interval_number = update_order_status_cron_exist.interval_number or False
            self.shopify_order_status_interval_type = update_order_status_cron_exist.interval_type or False
            self.shopify_order_status_next_execution = update_order_status_cron_exist.nextcall or False
            self.shopify_order_status_user_id = update_order_status_cron_exist.user_id.id or False

    def update_payout_report_cron_field(self, instance):
        """
        Update and set the 'Update Payout Report' cron field while open the wizard
        :param instance:
        :return:
        @author: Deval Jagad on date 16/11/2019.
        """
        try:
            payout_report_cron_exist = instance and self.env.ref(
                'shopify_ept.ir_cron_auto_import_payout_report_instance_%d' % instance.id)
        except:
            payout_report_cron_exist = False
        try:
            auto_process_bank_statement_cron_exist = instance and self.env.ref(
                'shopify_ept.ir_cron_auto_process_bank_statement_instance_%d' % instance.id)
        except:
            auto_process_bank_statement_cron_exist = False

        if payout_report_cron_exist and payout_report_cron_exist.active:
            self.shopify_auto_import_payout_report = payout_report_cron_exist.active
            self.shopify_payout_import_interval_number = payout_report_cron_exist.interval_number or False
            self.shopify_payout_import_interval_type = payout_report_cron_exist.interval_type or False
            self.shopify_payout_import_next_execution = payout_report_cron_exist.nextcall or False
            self.shopify_payout_import_user_id = payout_report_cron_exist.user_id.id or False
        if auto_process_bank_statement_cron_exist and auto_process_bank_statement_cron_exist.active:
            self.shopify_auto_process_bank_statement = auto_process_bank_statement_cron_exist.active
            self.shopify_auto_process_bank_statement_interval_number = auto_process_bank_statement_cron_exist.interval_number or False
            self.shopify_auto_process_bank_statement_interval_type = auto_process_bank_statement_cron_exist.interval_type or False
            self.shopify_auto_process_bank_statement_next_execution = auto_process_bank_statement_cron_exist.nextcall or False
            self.shopify_auto_process_bank_statement_user_id = auto_process_bank_statement_cron_exist.user_id.id or False

    def save(self):
        """
        Save method for auto cron
        @author: Angel Patel @Emipro Technologies Pvt. Ltd on date 16/11/2019.
        Task Id : 157716
        """
        instance = self.shopify_instance_id
        self.setup_shopify_inventory_export_cron(instance)
        self.setup_shopify_import_order_cron(instance)
        self.setup_shopify_update_order_status_cron(instance)
        self.setup_shopify_payout_report_cron(instance)
        if self._context.get('is_calling_from_onboarding_panel', False):
            if not instance:
                instance = self.shopify_instance_id
            if instance:
                action = self.env["ir.actions.actions"]._for_xml_id(
                    "shopify_ept.shopify_onboarding_confirmation_wizard_action")
                action['context'] = {'shopify_instance_id': instance.id}
                return action
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def setup_shopify_inventory_export_cron(self, instance):
        """
        Cron for auto Export Inventory Stock
        :param instance:
        :return:
        @author: Angel Patel @Emipro Technologies Pvt. Ltd on date 16/11/2019.
        Task Id : 157716
        """
        try:
            cron_exist = self.env.ref(
                'shopify_ept.ir_cron_shopify_auto_export_inventory_instance_%d' % instance.id)
        except:
            cron_exist = False
        if self.shopify_stock_auto_export:
            nextcall = datetime.now() + _intervalTypes[self.shopify_inventory_export_interval_type](
                self.shopify_inventory_export_interval_number)
            vals = {'active': True,
                    'interval_number': self.shopify_inventory_export_interval_number,
                    'interval_type': self.shopify_inventory_export_interval_type,
                    'nextcall': self.shopify_inventory_export_next_execution or nextcall.strftime('%Y-%m-%d %H:%M:%S'),
                    'code': "model.update_stock_in_shopify(ctx={'shopify_instance_id':%d})" % instance.id,
                    'user_id': self.shopify_inventory_export_user_id and self.shopify_inventory_export_user_id.id}

            if cron_exist:
                vals.update({'name': cron_exist.name})
                cron_exist.write(vals)
            else:
                core_cron = self.check_core_shopify_cron("shopify_ept.ir_cron_shopify_auto_export_inventory")

                name = instance.name + ' : ' + core_cron.name
                vals.update({'name': name})
                new_cron = core_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module': 'shopify_ept',
                                                  'name': 'ir_cron_shopify_auto_export_inventory_instance_%d' % (
                                                      instance.id),
                                                  'model': 'ir.cron',
                                                  'res_id': new_cron.id,
                                                  'noupdate': True
                                                  })

        else:
            if cron_exist:
                cron_exist.write({'active': False})
            return True

    def setup_shopify_import_order_cron(self, instance):
        """
        Cron for auto Import Orders
        :param instance:
        :return:
        @author: Angel Patel @Emipro Technologies Pvt. Ltd on date 16/11/2019.
        Task Id : 157716
        """
        try:
            cron_exist = self.env.ref('shopify_ept.ir_cron_shopify_auto_import_order_instance_%d' % instance.id)
        except:
            cron_exist = False
        if self.shopify_order_auto_import:
            nextcall = datetime.now() + _intervalTypes[self.shopify_import_order_interval_type](
                self.shopify_import_order_interval_number)
            vals = {'active': True,
                    'interval_number': self.shopify_import_order_interval_number,
                    'interval_type': self.shopify_import_order_interval_type,
                    'nextcall': self.shopify_import_order_next_execution or nextcall.strftime('%Y-%m-%d %H:%M:%S'),
                    'code': "model.import_order_cron_action(ctx={'shopify_instance_id':%d})" % instance.id,
                    'user_id': self.shopify_import_order_user_id and self.shopify_import_order_user_id.id}
            if cron_exist:
                vals.update({'name': cron_exist.name})
                cron_exist.write(vals)
            else:
                core_cron = self.check_core_shopify_cron("shopify_ept.ir_cron_shopify_auto_import_order")

                name = instance.name + ' : ' + core_cron.name
                vals.update({'name': name})
                new_cron = core_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module': 'shopify_ept',
                                                  'name': 'ir_cron_shopify_auto_import_order_instance_%d' % (
                                                      instance.id),
                                                  'model': 'ir.cron',
                                                  'res_id': new_cron.id,
                                                  'noupdate': True
                                                  })

        else:
            if cron_exist:
                cron_exist.write({'active': False})
        return True

    def setup_shopify_update_order_status_cron(self, instance):
        """
        Cron for auto Update Order Status
        :param instance:
        :return:
        @author: Angel Patel @Emipro Technologies Pvt. Ltd on date 16/11/2019.
        Task Id : 157716
        """
        try:
            cron_exist = self.env.ref(
                'shopify_ept.ir_cron_shopify_auto_update_order_status_instance_%d' % instance.id)
        except:
            cron_exist = False
        if self.shopify_order_status_auto_update:
            nextcall = datetime.now() + _intervalTypes[self.shopify_order_status_interval_type](
                self.shopify_order_status_interval_number)
            vals = {'active': True,
                    'interval_number': self.shopify_order_status_interval_number,
                    'interval_type': self.shopify_order_status_interval_type,
                    'nextcall': self.shopify_order_status_next_execution or nextcall.strftime('%Y-%m-%d %H:%M:%S'),
                    'code': "model.update_order_status_cron_action(ctx={'shopify_instance_id':%d})" % instance.id,
                    'user_id': self.shopify_order_status_user_id and self.shopify_order_status_user_id.id}
            if cron_exist:
                vals.update({'name': cron_exist.name})
                cron_exist.write(vals)
            else:
                core_cron = self.check_core_shopify_cron("shopify_ept.ir_cron_shopify_auto_update_order_status")

                name = instance.name + ' : ' + core_cron.name
                vals.update({'name': name})
                new_cron = core_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module': 'shopify_ept',
                                                  'name': 'ir_cron_shopify_auto_update_order_status_instance_%d' % (
                                                      instance.id),
                                                  'model': 'ir.cron',
                                                  'res_id': new_cron.id,
                                                  'noupdate': True
                                                  })

        else:
            if cron_exist:
                cron_exist.write({'active': False})
            return True

    def setup_shopify_payout_auto_import_payout_report_cron(self, instance):
        """
        Author: Deval Jagad (02/06/2020)
        Task Id : 163887
        Func: this method use for the create import payout report instance wise cron or set active
        :param instance:use for shopify instance
        :return:True
        """
        try:
            cron_exist = self.env.ref(
                'shopify_ept.ir_cron_auto_import_payout_report_instance_%d' % instance.id)
        except:
            cron_exist = False

        nextcall = datetime.now() + _intervalTypes[self.shopify_payout_import_interval_type](
            self.shopify_payout_import_interval_number)
        vals = {'active': True,
                'interval_number': self.shopify_payout_import_interval_number,
                'interval_type': self.shopify_payout_import_interval_type,
                'nextcall': self.shopify_payout_import_next_execution or nextcall.strftime('%Y-%m-%d %H:%M:%S'),
                'code': "model.auto_import_payout_report(ctx={'shopify_instance_id':%d})" % instance.id,
                'user_id': self.shopify_payout_import_user_id and self.shopify_payout_import_user_id.id}

        if cron_exist:
            vals.update({'name': cron_exist.name})
            cron_exist.write(vals)
        else:
            core_cron = self.check_core_shopify_cron("shopify_ept.ir_cron_auto_import_payout_report")

            name = instance.name + ' : ' + core_cron.name
            vals.update({'name': name})
            new_cron = core_cron.copy(default=vals)
            self.env['ir.model.data'].create({'module': 'shopify_ept',
                                              'name': 'ir_cron_auto_import_payout_report_instance_%d' % (
                                                  instance.id),
                                              'model': 'ir.cron',
                                              'res_id': new_cron.id,
                                              'noupdate': True
                                              })
        return True

    def setup_shopify_payout_auto_process_bank_statement_cron(self, instance):
        """
        Author: Deval Jagad (02/06/2020)
        Task Id : 163887
        Func: this method use for the create process bank statement instance wise cron or set active
        :param instance: use for shopify instance
        :return: True
        """
        try:
            cron_exist = self.env.ref(
                'shopify_ept.ir_cron_auto_process_bank_statement_instance_%d' % instance.id)
        except:
            cron_exist = False
        nextcall = datetime.now() + _intervalTypes[self.shopify_auto_process_bank_statement_interval_type](
            self.shopify_auto_process_bank_statement_interval_number)
        vals = {'active': True,
                'interval_number': self.shopify_auto_process_bank_statement_interval_number,
                'interval_type': self.shopify_auto_process_bank_statement_interval_type,
                'nextcall': self.shopify_auto_process_bank_statement_next_execution or nextcall.strftime(
                    '%Y-%m-%d %H:%M:%S'),
                'code': "model.auto_process_bank_statement(ctx={'shopify_instance_id':%d})" % instance.id,
                'user_id': self.shopify_auto_process_bank_statement_user_id and self.shopify_auto_process_bank_statement_user_id.id}
        if cron_exist:
            vals.update({'name': cron_exist.name})
            cron_exist.write(vals)
        else:
            core_cron = self.check_core_shopify_cron("shopify_ept.ir_cron_auto_process_bank_statement")

            name = instance.name + ' : ' + core_cron.name
            vals.update({'name': name})
            new_cron = core_cron.copy(default=vals)
            self.env['ir.model.data'].create({'module': 'shopify_ept',
                                              'name': 'ir_cron_auto_process_bank_statement_instance_%d' % (
                                                  instance.id),
                                              'model': 'ir.cron',
                                              'res_id': new_cron.id,
                                              'noupdate': True
                                              })
        return True

    def setup_shopify_payout_report_cron(self, instance):
        if self.shopify_auto_import_payout_report:
            self.setup_shopify_payout_auto_import_payout_report_cron(instance)
        else:
            try:
                cron_exist = self.env.ref(
                    'shopify_ept.ir_cron_auto_import_payout_report_instance_%d' % instance.id)
            except:
                cron_exist = False
            if cron_exist:
                cron_exist.write({'active': False})

        if self.shopify_auto_process_bank_statement:
            self.setup_shopify_payout_auto_process_bank_statement_cron(instance)
        else:
            try:
                cron_exist = self.env.ref(
                    'shopify_ept.ir_cron_auto_process_bank_statement_instance_%d' % instance.id)
            except:
                cron_exist = False
            if cron_exist:
                cron_exist.write({'active': False})
        return True

    @api.model
    def action_shopify_open_cron_configuration_wizard(self):
        """
           Usage: Return the action for open the cron configuration wizard
           @Task:   166992 - Shopify Onboarding panel
           @author: Dipak Gogiya
           :return: True
        """
        """ Called by onboarding panel above the Instance."""
        action = self.env["ir.actions.actions"]._for_xml_id(
            "shopify_ept.action_wizard_shopify_cron_configuration_ept")
        instance = self.env['shopify.instance.ept'].search_shopify_instance()
        action['context'] = {'is_calling_from_onboarding_panel': True}
        if instance:
            action.get('context').update({'default_shopify_instance_id': instance.id,
                                          'is_instance_exists': True})
        return action

    def check_core_shopify_cron(self, name):
        """
        This method will check for the core cron and if doesn't exist, then raise error.
        @author: Maulik Barad on Date 28-Sep-2020.
        @param name: Name of the core cron.
        """
        try:
            core_cron = self.env.ref(name)
        except:
            core_cron = False

        if not core_cron:
            raise UserError(
                'Core settings of Shopify are deleted, please upgrade Shopify module to back this settings.')
        return core_cron
