
import frappe
import os

def execute():
    # 1. Create Dashboard Chart Source DocType record
    source_name = "Satis Analytics"
    module = "ArchERP" # App name
    
    if not frappe.db.exists("Dashboard Chart Source", source_name):
        doc = frappe.new_doc("Dashboard Chart Source")
        doc.name = source_name
        doc.source_name = source_name
        doc.module = module
        doc.timeseries = 1 # We want a timeseries chart
        doc.insert()
        frappe.db.commit()
        print(f"Created Dashboard Chart Source: {source_name}")
    else:
        print(f"Dashboard Chart Source {source_name} already exists.")
        
    # 2. Update the Chart 'Satis Trendi' (or 'Satış Trendi')
    # Using 'like' to match unicode/ascii differences if any
    charts = frappe.get_all("Dashboard Chart", filters={"chart_name": ["like", "Sat%Trend%"]}, pluck="name")
    
    if charts:
        for chart_name in charts:
            # Use set_value to bypass 'set_only_once' validation
            frappe.db.set_value("Dashboard Chart", chart_name, "chart_type", "Custom")
            frappe.db.set_value("Dashboard Chart", chart_name, "source", source_name)
            frappe.db.set_value("Dashboard Chart", chart_name, "document_type", None)
            frappe.db.set_value("Dashboard Chart", chart_name, "based_on", None)
            frappe.db.set_value("Dashboard Chart", chart_name, "value_based_on", None)
            
            print(f"Updated Chart '{chart_name}' to use Source '{source_name}'")
        frappe.db.commit()
    else:
        print("Chart 'Satış Trendi' not found.")

if __name__ == "__main__":
    execute()
