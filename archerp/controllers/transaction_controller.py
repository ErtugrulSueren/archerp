
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class TransactionController(Document):
    def validate(self):
        if self.docstatus == 0:
            self.calculate_totals()

    def calculate_totals(self):
        total_net = 0.0
        total_tax = 0.0
        # Default to 0 if field missing, safe for all doctypes
        tax_inclusive_field = getattr(self, "vergi_dahil_mi", 0)
        tax_inclusive = tax_inclusive_field == 1
        
        # Check if 'kalemler' exists (child table)
        if not hasattr(self, "kalemler"):
            return

        for item in self.kalemler:
            qty = flt(item.miktar)
            price = flt(item.birim_fiyat)
            tax_rate = flt(item.vergi_orani)
            discount_rate = flt(getattr(item, "iskonto_orani", 0))

            # Apply Discount
            # Assuming discount is percentage on price
            if discount_rate > 0:
                discount_amount_per_unit = price * (discount_rate / 100.0)
                price = price - discount_amount_per_unit
                # Set calculated discount amount field if exists
                if hasattr(item, "iskonto_tutari"):
                    item.iskonto_tutari = discount_amount_per_unit * qty

            # Fetch default accounts if missing (Hizmet/Stok logic)
            # Use getattr to safely check for 'muhasebe_hesabi' as it might not affect all child tables (e.g. Offers)
            current_account = getattr(item, "muhasebe_hesabi", None)
            
            if item.tur == "Hizmet" and hasattr(item, "gelir_gider_kalemi") and not current_account:
                 default_acc = frappe.db.get_value("Gelir Gider Kalemi", item.gelir_gider_kalemi, "varsayilan_hesap")
                 if default_acc and hasattr(item, "muhasebe_hesabi"):
                     item.muhasebe_hesabi = default_acc
            
            elif item.tur != "Hizmet" and hasattr(item, "urun") and not current_account:
                 # Only try to fetch if we define product
                 default_acc = frappe.db.get_value("Urun", item.urun, "gider_hesabi")
                 if default_acc and hasattr(item, "muhasebe_hesabi"):
                     item.muhasebe_hesabi = default_acc

            # Tax Calculation
            if tax_inclusive:
                net_unit_price = price / (1 + (tax_rate / 100.0))
                unit_tax = price - net_unit_price
            else:
                net_unit_price = price
                unit_tax = net_unit_price * (tax_rate / 100.0)
            
            line_net = qty * net_unit_price
            line_tax = qty * unit_tax
            
            item.tutar = line_net
            
            total_net += line_net
            total_tax += line_tax
            
        self.ara_toplam = total_net
        self.vergi_toplami = total_tax
        
        # Additional Global Discount
        discount = flt(getattr(self, "ek_iskonto_tutari", 0))
        grand_total = total_net + total_tax - discount
        
        if grand_total < 0:
            grand_total = 0.0
            
        self.genel_toplam = grand_total
        
        # Base Currency Calculation (TL Equivalent)
        # Using exchange rate to convert transaction currency to base currency
        exchange_rate = flt(getattr(self, "doviz_kuru", 1.0))
        if exchange_rate <= 0: 
            exchange_rate = 1.0
            
        base_total = grand_total * exchange_rate
        
        # Support both naming conventions just in case
        if hasattr(self, "base_genel_toplam"):
            self.base_genel_toplam = base_total
        elif hasattr(self, "base_grand_total"):
            self.base_grand_total = base_total

    def create_gl_entry(self, account, debit, credit, cancel, party_type=None, party=None, remark=None):
        from archerp.controllers.general_ledger import create_gl_entry
        create_gl_entry(self, account, debit, credit, cancel, party_type, party, remark)

@frappe.whitelist()
def calculate_doc(doc):
    if isinstance(doc, str):
        doc = frappe.parse_json(doc)
        
    # Instantiate without saving
    d = frappe.get_doc(doc)
    
    # Ensure it treats it as the correct logic (validate calls calculate_totals)
    if hasattr(d, 'calculate_totals'):
        d.calculate_totals()
        
    return d
