
import frappe
from frappe.utils import flt, getdate

# Satış Kartları ve Grafikleri için Backend Kodları
# Örn: archerp.dashboard.satis.get_pending_orders

@frappe.whitelist()
def get_total_revenue(filters=None):
    """
    Calculates Total Revenue (base_grand_total) for allowed Sales Invoices.
    Bypasses strict field-level permissions but respects Document permissions.
    """
    # 1. Get allowed invoice names (Standard Permission Check)
    # This automatically filters by User Permissions, Role Permissions etc.
    allowed_invoices = frappe.get_list("Satis Faturasi", pluck="name")
    
    if not allowed_invoices:
        return 0.0
        
    # 2. Sum the base_grand_total for these invoices
    sf = frappe.qb.DocType("Satis Faturasi")
    from frappe.query_builder.functions import Sum
    
    query = (
        frappe.qb.from_(sf)
        .select(Sum(sf.base_grand_total))
        .where(sf.name.isin(allowed_invoices))
        .where(sf.docstatus == 1) # Only Submitted Invoices usually count for Revenue
    )
    
    result = query.run()
    return flt(result[0][0]) if result and result[0][0] else 0.0
