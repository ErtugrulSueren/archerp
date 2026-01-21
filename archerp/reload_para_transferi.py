import frappe

def execute():
    frappe.reload_doc("finans", "doctype", "para_transferi")
    frappe.db.commit()
    print("Para Transferi reloaded successfully.")
