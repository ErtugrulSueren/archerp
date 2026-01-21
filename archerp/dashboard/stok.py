
import frappe
from frappe.utils import flt

@frappe.whitelist()
def get_critical_stock_count(filters=None):
    """
    Returns the count of active items where current stock <= critical stock level.
    Only considers items where critical_stock > 0.
    """
    # Modern Logic (Query Builder):
    # 1. Get permitted warehouses using standard ORM (handles permissions automatically)
    allowed_warehouses = frappe.get_list("Depo", pluck="name")
    
    if not allowed_warehouses:
        return 0
        
    # 2. Build Query
    sb = frappe.qb.DocType("Stok Bakiyesi")
    u = frappe.qb.DocType("Urun")
    from frappe.query_builder.functions import Sum, Max, Count
    
    query = (
        frappe.qb.from_(sb)
        .inner_join(u).on(sb.urun == u.name)
        .select(Count("*"))
        .where(u.aktif_mi == 1)
        .where(u.kritik_stok > 0)
        .where(sb.depo.isin(allowed_warehouses))
        .groupby(sb.urun)
        .having(Sum(sb.mevcut_miktar) <= Max(u.kritik_stok))
    )
    
    # Run: The result is a list of grouped counts. Usage of Count("*") inside specific grouping logic
    # might act differently. We want the COUNT of groups that satisfy the HAVING condition.
    # Standard SQL: SELECT COUNT(*) FROM (SELECT ... HAVING ...)
    
    # Optimization: QB doesn't support "COUNT from subquery" easily in one chain.
    # We will fetch the groups and count them in Python (len).
    # Since this is "Critical Items", the expected number is low (5-50 items).
    
    query = (
        frappe.qb.from_(sb)
        .inner_join(u).on(sb.urun == u.name)
        .select(sb.urun)
        .where(u.aktif_mi == 1)
        .where(u.kritik_stok > 0)
        .where(sb.depo.isin(allowed_warehouses))
        .groupby(sb.urun)
        .having(Sum(sb.mevcut_miktar) <= Max(u.kritik_stok))
    )
    
    result = query.run()
    return len(result)

@frappe.whitelist()
def get_critical_items_list(filters=None):
    """
    Returns the list of critical items for a table/chart.
    """
    # Modern Standard: Use Frappe Query Builder
    table = frappe.qb.DocType("Urun")
    query = (
        frappe.qb.from_(table)
        .select(table.urun_adi, table.mevcut_stok, table.kritik_stok)
        .where(table.aktif_mi == 1)
        .where(table.kritik_stok > 0)
        .where(table.mevcut_stok <= table.kritik_stok)
        .orderby(table.mevcut_stok, order=frappe.qb.asc)
        .limit(10)
    )
    
    return query.run(as_dict=True)

@frappe.whitelist()
def get_total_stock_value(filters=None):
    """
    Returns the total valuation amount of stock in permitted warehouses.
    """
    allowed_warehouses = frappe.get_list("Depo", pluck="name")
    
    if not allowed_warehouses:
        return 0.0
        
    sb = frappe.qb.DocType("Stok Bakiyesi")
    from frappe.query_builder.functions import Sum
    
    query = (
        frappe.qb.from_(sb)
        .select(Sum(sb.degerleme_tutari))
        .where(sb.depo.isin(allowed_warehouses))
    )
    
    result = query.run()
    return flt(result[0][0]) if result and result[0][0] else 0.0
