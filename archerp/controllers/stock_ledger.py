import frappe
from frappe.utils import flt

def create_stock_entry(doc, item, qty, reverse=False, warehouse_field="depo"):
    """
    Creates a Stock Ledger (Stok Defteri) Entry.
    
    Args:
        doc (Document): The parent document (self).
        item (Document/Dict): The line item containing product info.
        qty (float): The quantity change (positive or negative).
                     - Negative: Out (Sales, Issue)
                     - Positive: In (Purchase, Receipt)
        reverse (bool): If True, multiplies quantity by -1 (for Cancellation).
        warehouse_field (str): Fieldname for the warehouse in the item. Defaults to 'depo'.
    """
    
    # 1. Calculate Final Quantity Change
    # qty comes in with sign (e.g. -5 for sales, +10 for purchase)
    # reverse flips it (e.g. +5 for cancelled sales)
    change = flt(qty)
    if reverse:
        change = change * -1
        
    if change == 0:
        return

    # 2. Create Entry
    stock_entry = frappe.new_doc("Stok Defteri")
    stock_entry.belge_tipi = doc.doctype
    stock_entry.belge_no = doc.name
    stock_entry.tarih = doc.tarih
    stock_entry.urun = item.urun
    
    # Warehouse Logic
    # Some items might have specific warehouse, or fall back to parent header
    # But usually item has the warehouse.
    warehouse = item.get(warehouse_field)
    
    # Fallback to parent if item has no warehouse (unlikely for well-designed docs but safe)
    if not warehouse and hasattr(doc, warehouse_field):
        warehouse = getattr(doc, warehouse_field)
    elif not warehouse and hasattr(doc, "hedef_depo"):
         warehouse = doc.hedef_depo
         
    if not warehouse:
        frappe.throw(f"Stok Hareketi için depo bulunamadı! Belge: {doc.name}, Ürün: {item.urun}")

    stock_entry.depo = warehouse
    stock_entry.birim = item.get("stok_birimi") or item.get("uom")

    stock_entry.degisim_miktari = change
    
    if change > 0:
        stock_entry.giren_miktar = change
        stock_entry.cikan_miktar = 0
    else:
        stock_entry.giren_miktar = 0
        stock_entry.cikan_miktar = abs(change)
        
    # 3. Cost Logic
    # Try to find unit cost in item
    unit_cost = flt(item.get("birim_maliyet") or item.get("birim_fiyat") or 0)
    
    # If 0, try fetching from Item Master (Standard Cost / Buying Price)
    if unit_cost == 0:
         unit_cost = flt(frappe.db.get_value("Urun", item.urun, "standart_alis_fiyati"))
    
    stock_entry.birim_maliyet = unit_cost
    stock_entry.toplam_tutar = unit_cost * abs(change)
    
    stock_entry.insert(ignore_permissions=True)
