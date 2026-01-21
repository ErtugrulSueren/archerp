import frappe

def execute():
    # Reload Urun
    frappe.reload_doc("stok", "doctype", "urun")
    
    # Reload Child Tables
    docs = [
        ("satis", "satis_kalemi"),
        ("satis", "teslimat_kalemi"),
        ("satis", "fatura_kalemi"),
        ("satin_alma", "satin_alma_fatura_kalemi"),
        ("stok", "mal_kabul_kalemi"),
        ("satin_alma", "satin_alma_kalemi")
    ]
    
    for module, doctype in docs:
        print(f"Reloading {module} -> {doctype}...")
        frappe.reload_doc(module, "doctype", doctype)
        
    frappe.db.commit()
    print("Schema update complete.")
