
import frappe
from frappe.utils import flt

def execute():
    doctypes = ["Satis Faturasi", "Satin Alma Faturasi"]
    
    for dt in doctypes:
        if not frappe.db.exists("DocType", dt):
            continue
            
        print(f"--- Updating {dt} ---")
        
        # Detect field name dynamically
        meta = frappe.get_meta(dt)
        if meta.has_field("base_grand_total"):
            target_field = "base_grand_total"
        elif meta.has_field("base_genel_toplam"):
            target_field = "base_genel_toplam"
        else:
            print(f"Skipping {dt}: No base total field found.")
            continue
            
        docs = frappe.get_all(dt, fields=["name", "genel_toplam", "doviz_kuru"])
        
        count = 0
        for d in docs:
            rate = flt(d.doviz_kuru)
            if rate <= 0: rate = 1.0
            
            base_val = flt(d.genel_toplam) * rate
            
            frappe.db.set_value(dt, d.name, target_field, base_val)
            count += 1
            
        print(f"Updated {count} records in {dt}")
        
    frappe.db.commit()
