
import frappe
import json

def execute():
    try:
        doc = frappe.get_doc("Number Card", "Toplam Ciro")
        print(json.dumps({
            "name": doc.name,
            "type": doc.type,
            "method": doc.method,
            "document_type": doc.document_type,
            "aggregate_function_based_on": doc.aggregate_function_based_on
        }, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    execute()
