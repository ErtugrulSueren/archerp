
import frappe

def execute():
    """
    Fixes the 'Toplam Ciro' Number Card to use the Custom Method that bypasses field permissions.
    """
    card_name = "Toplam Ciro"
    
    if not frappe.db.exists("Number Card", card_name):
        print(f"Card {card_name} not found.")
        return

    doc = frappe.get_doc("Number Card", card_name)
    
    # Update to Custom Type
    doc.type = "Custom"
    doc.method = "archerp.dashboard.satis.get_total_revenue"
    
    # Clear standard fields to avoid confusion
    doc.document_type = None
    doc.aggregate_function_based_on = None
    doc.function = None
    
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    print(f"Successfully updated '{card_name}' to use custom revenue function.")

if __name__ == "__main__":
    execute()
