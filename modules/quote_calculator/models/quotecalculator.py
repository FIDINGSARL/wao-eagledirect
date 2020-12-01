# import the files

from odoo import api, fields, models


class QuoteCalculator_purchase(models.Model):
    _inherit = 'purchase.order'
    dealer_discount = fields.Float(string = 'Dealer Discount')
    freight_supplier_currency = fields.Float(string = 'Freight Supplier Currency')
    commissioning = fields.Float(string = 'Commissioning')	
    design_engineering = fields.Float(string = 'Design Engineering')
    handlings = fields.Float(string = 'Handlings')
    custom_value = fields.Float(string = 'Custom')
    line_items = fields.One2many('purchase.order.line', 'order_id', string='Order Line Items')
    dealer_price = fields.Float(string='Purchase Price', compute = '_calPrice', store = True)
    fixed_currency_rate = fields.Float(string = 'Fixed Currency Rate')

    @api.depends('line_items.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            other_amount = order.freight_supplier_currency + order.commissioning + order.design_engineering + order.handlings + order.custom_value
            for line in order.order_line:
                line._compute_amount()
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax + other_amount,
            })

    @api.depends('line_items', 'dealer_discount')
    def _calPrice(self):
        for orderitems in self:
            discount = orderitems.dealer_discount
            for line in orderitems.line_items:
                line.dealer_purchase_price = line.price_unit*(1 - discount)
    
    # create button "Create Sales Order" in Purchase
    def create_sales_order(self):
        # order_reference = self.name

        line_items_vals = []
        for line in self.line_items:
            line_items_vals.append({
                'product_id': line.product_id.id,
                'name':line.name,
                'product_uom_qty':line.product_qty,
                'price_unit':line.price_unit
            })

        vals = {
            'partner_id' : self.partner_id.id,  
            'freight_supplier_currency' : self.freight_supplier_currency,
            'design_engineering' : self.design_engineering,
            'commissioning' : self.commissioning,
            'handlings' : self.handlings,
            'custom_value' : self.custom_value,
            'order_line' : [(0, 0, invoice_line_id) for invoice_line_id in line_items_vals]
        }

        # print("**************************************** ******************************************")
        # print(self.partner_id.id)

        view_ref = self.env['ir.model.data'].get_object_reference('sale', 'view_order_form')
        view_id = view_ref[1] if view_ref else False

        new_salesorder = self.env['sale.order'].create(vals)
    
        view_data = {
        'type': 'ir.actions.act_window',
        'name': ('Sales Order'),
        'res_model': 'sale.order',
        'res_id': new_salesorder.id,
        'view_type': 'form',
        'view_mode': 'form',
        'view_id': view_id,
        'target': 'new'
        }

        return view_data

class QuoteCalculator_purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'
    dealer_purchase_price = fields.Float(string='Dealer Purchase Price')


    @api.depends('product_qty', 'price_unit', 'taxes_id','dealer_purchase_price')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            dealer_price = line.dealer_purchase_price
            taxes = line.taxes_id.compute_all(
                dealer_price,
                vals['currency_id'],
                vals['product_qty'],
                vals['product'],
                vals['partner'])
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

class QuoteCalculator_SalesOrder(models.Model):
    _inherit = "sale.order"
    _description = "Sale Order"

    margin = fields.Float(string = 'Margin')

    freight = fields.Float(string = 'Freight')
    exchange_rate = fields.Float(string ='Exchange Rate')
    cost_aud_per_unit = fields.Float(string = 'Cost AUD per Unit', compute ='_calCost', store =True)
    line_items = fields.One2many('sale.order.line', 'order_id', string='Order Lines Items')

    design_engineering = fields.Float(string = 'Desing Engineering')
    margin_supply_charges = fields.Float(string = 'Margin Supply Charges')
    commissioning = fields.Float(string = 'Commissioning')	
    freight_supplier_currency = fields.Float(string = 'Freight Supplier Currency')
    handlings = fields.Float(string = 'Handlings')
    custom_value = fields.Float(string = 'Custom')

    @api.depends('design_engineering','margin_supply_charges', 'exchange_rate')
    def _cal_design_engineering(self):
        for orders in self:
            orders.calculated_design_engineering = (orders.design_engineering * (1 + orders.margin_supply_charges) * (1/(orders.exchange_rate - 0.005)))

    calculated_design_engineering = fields.Float(string = 'Design Engineering', compute = '_cal_design_engineering', store = True)

    margin_local_charges = fields.Float(string = 'Margin Local Charges')
    local_customs_value = fields.Float(string = 'Customs')
    destination_charges = fields.Float(string = 'Destination Charges')
    local_freight = fields.Float(string = 'Local Freight')


    retail_discount = fields.Float(string='Retail Disocunt')

    @api.depends('line_items', 'retail_discount')
    def _cal_retail_discount(self):
        for orders in self:
            compute_price = 0
            exc_rate = orders.exchange_rate
            margin_val = orders.margin
            freight_val = orders.freight
            retail_discount = orders.retail_discount
            for line in orders.line_items:
                compute_price = (line.price_unit * line.product_uom_qty * (1/ (exc_rate - 0.005))) * (retail_discount + ((retail_discount - (retail_discount/(1+ margin_val) * (1 + freight_val )))) + 0.005)
            orders.computed_retail_discount = (-1 * compute_price)
    
    computed_retail_discount = fields.Float(string='Total Retail Discount', compute = '_cal_retail_discount', store = True) 

       
    
    @api.depends('amount_total')
    def _calGst(self):
        for orders in self:
            orders.gst_value = orders.amount_total * 0.1
    
    gst_value = fields.Float(string='GST', compute = '_calGst' , store = True)

    @api.depends('line_items.aud_total')
    def _cal_subtotal(self):
        for orders in self:
            subtotal = 0
            for line in orders.line_items:
                subtotal = subtotal + line.aud_total
            orders.subtotal_value = subtotal

    subtotal_value = fields.Float(string = 'Sub Total with AUD', compute = '_cal_subtotal', store = True)

    @api.depends('line_items', 'local_freight', 'local_customs_value', 'destination_charges', 'margin_local_charges')
    def _calLocal_destintaion_charges(self):
        for orders in self:
            margin_local_charges = orders.margin_local_charges
            local_freight = orders.local_freight
            local_customs_value = orders.local_customs_value
            destination_charges = orders.destination_charges
            orders.local_destination_charges = (local_freight + local_customs_value + destination_charges) *  (1 + margin_local_charges)

    local_destination_charges = fields.Float(string = 'LOCAL DESTINATION CHARGES', compute = '_calLocal_destintaion_charges', store = True)

    @api.depends('design_engineering', 'subtotal_value','margin_supply_charges', 'commissioning','freight_supplier_currency','handlings', 'exchange_rate')
    def _cal_shipping_insurance(self):
        for orders in self:
            orders.shipping_insurance = (
            orders.subtotal_value + (-1 * (orders.subtotal_value * orders.retail_discount)) +
            (orders.freight_supplier_currency * (1 + orders.margin_supply_charges))/(orders.exchange_rate - 0.005) + 
            (orders.handlings * (1 + orders.margin_supply_charges))/(orders.exchange_rate - 0.005) +
            (orders.design_engineering * (1 + orders.margin_supply_charges))/(orders.exchange_rate - 0.005) + 
            (orders.commissioning * (1 + orders.margin_supply_charges))/(orders.exchange_rate - 0.005) ) * 0.005
            # orders.shipping_insurance = (orders.subtotal_value + orders.computed_retail_discount + orders.calculated_design_engineering)*0.005 

    shipping_insurance = fields.Float(string = 'Shipping Insurance', compute = '_cal_shipping_insurance', store = True)

    @api.depends('amount_total','gst_value')
    def _cal_total_ince_gst(self):
        for orders in self:
            orders.total_inc_gst = orders.amount_total + orders.gst_value

    total_inc_gst = fields.Float(string = 'Total Inc GST', compute = '_cal_total_ince_gst', store = True)
    
    @api.depends('line_items.price_total','local_destination_charges','shipping_insurance','calculated_design_engineering')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            other_amount = order.local_destination_charges + order.computed_retail_discount + order.calculated_design_engineering + order.shipping_insurance
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax + other_amount,
            })

    @api.depends('line_items','exchange_rate')
    def _calCost(self):
        for orderitems in self:
            exc = 0
            #cost_aud_per_unit_val = 0
            exc_rate = orderitems.exchange_rate
            margin_val = orderitems.margin
            freight_val = orderitems.freight
            for line in orderitems.line_items:
                EXC = 1/(exc_rate - 0.005)
                cost_aud_per_unit_val = line.cost_aud_per_unit1 = EXC * line.price_unit
                aud_marginvalue = line.aud_unit_price_with_margin = cost_aud_per_unit_val * (1 + margin_val)
                AUD_Freight = (line.price_unit * EXC * (1 + margin_val)) * freight_val
                aud_per_unit = line.aud_unit_total = aud_marginvalue + AUD_Freight
                line.aud_total = aud_per_unit * line.product_uom_qty

class QuoteCalculator_SalesOrderLine(models.Model):
    _inherit = "sale.order.line"
    cost_aud_per_unit1 = fields.Float(string = 'Cost AUD per Unit')
    aud_unit_price_with_margin = fields.Float(string = 'AUD Unit PRICE with Margin')
    aud_per_unit = fields.Float(string = 'AUD per UNIT')
    aud_unit_total = fields.Float(string = 'AUD UNIT TOTAL')
    aud_total = fields.Float(string = 'AUD TOTAL')

    @api.depends('product_uom_qty', 'discount', 'aud_unit_total', 'tax_id')
    def _compute_amount(self):
        for line in self:
            price = line.aud_unit_total * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups('account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])
			
class QuoteCalculator_Account_Move(models.Model):
    _inherit = "account.move"
    
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order Id')

    purchase_ref = fields.Float(related = 'purchase_order_id.name', string = 'Ref', store = True)

    @api.depends('purchase_order_id')
    def _cal_fixed_currency_rate(self):
        for record in self:
            record.fixed_currency_rate_bill = record.purchase_order_id.fixed_currency_rate

    fixed_currency_rate_bill = fields.Float(string = 'Fixed Currency Rate', digits = (12, 4), compute = "_cal_fixed_currency_rate", store = True)
    
    fixed_rate = fields.Float(related = 'purchase_order_id.fixed_currency_rate', store = True)




    
