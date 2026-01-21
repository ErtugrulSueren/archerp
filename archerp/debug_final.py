
import frappe

def execute():
    # 1. Check Valid Data
    print("--- 1. Data Check (Satis Faturasi) ---")
    fields = ["name", "genel_toplam", "doviz_kuru", "fatura_tarihi"]
    meta = frappe.get_meta("Satis Faturasi")
    
    if meta.has_field("base_grand_total"):
        fields.append("base_grand_total")
        print("Detected field: base_grand_total")
    if meta.has_field("base_genel_toplam"):
        fields.append("base_genel_toplam")
        print("Detected field: base_genel_toplam")
        
    invoices = frappe.get_all("Satis Faturasi", fields=fields, limit=5, order_by="creation desc")
    for inv in invoices:
        print(f"{inv}")

    # 2. Check Card Config
    print("\n--- 2. Card Check (Toplam Ciro) ---")
    if frappe.db.exists("Number Card", "Toplam Ciro"):
        card = frappe.get_doc("Number Card", "Toplam Ciro")
        print(f"Function: {card.function}")
        print(f"Aggregate Based On: {card.aggregate_function_based_on}")
        print(f"Filters: {card.filters_json}")

