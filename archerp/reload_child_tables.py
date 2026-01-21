import frappe

def execute():
    docs = [
        ("satis", "satis_kalemi"),
        ("satis", "siparis_kalemi"),
        ("satis", "teslimat_kalemi"),
        ("satis", "fatura_kalemi"),
        ("satin_alma", "satin_alma_teklif_kalemi"),
        ("satin_alma", "satin_alma_kalemi"),
        ("stok", "mal_kabul_kalemi"),
        ("satin_alma", "satin_alma_fatura_kalemi")
    ]
    
    for module, doctype in docs:
        print(f"Reloading {module} -> {doctype}...")
        frappe.reload_doc(module, "doctype", doctype)
        
    frappe.db.commit()
    print("All reloaded successfully.")
