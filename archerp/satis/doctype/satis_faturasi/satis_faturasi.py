import frappe
from frappe.utils import flt
from archerp.controllers.transaction_controller import TransactionController

class SatisFaturasi(TransactionController):
    def validate(self):
        # 1. Assign Income Accounts automatically if missing
        for item in self.kalemler:
            if not item.muhasebe_hesabi:
                if item.tur == "Stok" and item.urun:
                    # Fetch 'gelir_hesabi' from Urun for Sales
                    item.muhasebe_hesabi = frappe.db.get_value("Urun", item.urun, "gelir_hesabi")
                elif item.tur == "Hizmet" and item.gelir_gider_kalemi:
                     # Fetch 'varsayilan_hesap' from Gelir Gider Kalemi
                    item.muhasebe_hesabi = frappe.db.get_value("Gelir Gider Kalemi", item.gelir_gider_kalemi, "varsayilan_hesap")
        
        # 2. Call Parent Calculations (Totals, Taxes, Discounts)
        super().validate()

    def on_submit(self):
        self.make_gl_entries()
        
    def on_cancel(self):
        self.make_gl_entries(cancel=True)
        
    def make_gl_entries(self, cancel=False):
        # Debtor (Customer) - Debit
        # We use 'genel_toplam' which is the final Grand Total
        self.create_gl_entry(
            account=self.borc_hesabi,
            debit=self.genel_toplam,
            credit=0,
            cancel=cancel,
            party_type="Musteri",
            party=self.musteri
        )
        
        # Income and Taxes
        for item in self.kalemler:
            if flt(item.tutar) > 0:
                # 1. Income Account - Credit
                # item.tutar is the Net Amount (without tax, after discount) calculated by controller
                self.create_gl_entry(
                    account=item.muhasebe_hesabi,
                    debit=0,
                    credit=item.tutar,
                    cancel=cancel
                )
                
                # 2. Tax Account - Credit
                # We need to recalculate tax amount per line to attribute it to the correct tax account
                qty = flt(item.miktar)
                # Price logic must match controller exactly to ensure pennies add up
                # Controller: price = item.birim_fiyat; discount applied; then tax logic.
                price = flt(item.birim_fiyat)
                tax_rate = flt(item.vergi_orani)
                discount_rate = flt(getattr(item, "iskonto_orani", 0))
                
                # Apply Discount
                if discount_rate > 0:
                    discount_amount = price * (discount_rate / 100.0)
                    price = price - discount_amount
                    
                # Tax Calculation
                if self.vergi_dahil_mi:
                    net_unit_price = price / (1 + (tax_rate / 100.0))
                    unit_tax = price - net_unit_price
                else:
                    unit_tax = price * (tax_rate / 100.0)
                
                line_tax = qty * unit_tax
                
                if line_tax > 0:
                    # Fetch Tax Account from Template
                    tax_account = frappe.db.get_value("Vergi", item.vergi_sablonu, "hesap")
                    if tax_account:
                        self.create_gl_entry(
                            account=tax_account,
                            debit=0,
                            credit=line_tax,
                            cancel=cancel
                        )
