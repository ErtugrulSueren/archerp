
import frappe

def execute():
    try:
        frappe.reload_doc("satis", "doctype", "satis_faturasi", force=True)
        print("Successfully reloaded Satis Faturasi.")
    except Exception as e:
        print(f"Error reloading DocType: {e}")

if __name__ == "__main__":
    execute()
