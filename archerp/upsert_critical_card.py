
import frappe

def execute():
    card_name = "Kritik Stok"
    if not frappe.db.exists("Number Card", card_name):
        doc = frappe.new_doc("Number Card")
        doc.name = card_name
        doc.label = "Kritik Stok"
        print("Creating new card...")
    else:
        doc = frappe.get_doc("Number Card", card_name)
        print("Updating existing card...")

    doc.type = "Custom"
    doc.method = "archerp.dashboard.stok.get_critical_stock_count"
    doc.color = "#FF4136" # Red
    doc.show_percentage_stats = 0
    doc.stats_time_interval = "Monthly"
    
    # Save
    doc.save()
    frappe.db.commit()
    print("Kritik Stok configured successfully.")
