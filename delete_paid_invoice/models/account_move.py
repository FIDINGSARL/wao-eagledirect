from odoo import models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def force_delete_invoice_and_related_payment(self):
        types = self.mapped('move_type')
        if not self._context.get('force_delete'):
            raise UserError(_("You cannot delete an invoice. something went wrong force delete delete context"))
        for invoice in self:
            relatedpayments_list = self and invoice._get_reconciled_info_JSON_values() or []
            relatedpayments_ids = relatedpayments_list and map(lambda x: x['account_payment_id'],relatedpayments_list) or False
            relatedpayments_ids = relatedpayments_ids and self.env['account.payment'].browse(list(relatedpayments_ids)) or self.env['account.payment']
            if relatedpayments_ids:
                relatedpayments_ids.action_draft()
                relatedpayments_ids.write({'name':False})
                relatedpayments_ids.unlink()
        invoice_posted_cancel = self.filtered(lambda x : x.state in ['posted','cancel']) or self.env['account.move']
        invoice_draft = self.filtered(lambda x: x.state not in ['posted', 'cancel'])
        #draft invoice found in list view maybe
        if invoice_posted_cancel:
            invoice_posted_cancel.button_draft()
            invoice_posted_cancel.with_context(force_delete=True).unlink()
            invoice_draft.with_context(force_delete=True).unlink()
        return {
            'name': _('Invoices'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'views': [(self.env.ref('account.view_invoice_tree').id, 'tree'), (self.env.ref('account.view_move_form').id, 'form')],
            'domain': [('move_type', 'in', types)],
        }
