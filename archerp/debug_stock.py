
import frappe

def execute():
    print("--- Inspecting Products with Critical Stock Set ---")
    items = frappe.get_all("Urun", 
        filters={"kritik_stok": [">", 0]}, 
        fields=["name", "urun_adi", "mevcut_stok", "kritik_stok", "aktif_mi"]
    )
    
    for item in items:
        print(f"Product: {item.name} ({item.urun_adi}) | Stok: {item.mevcut_stok} | Kritik: {item.kritik_stok} | Aktif: {item.aktif_mi}")
        
    print("\n--- Testing Current Query Logic ---")
    try:
        count = frappe.db.count("Urun", filters={
            "aktif_mi": 1,
            "kritik_stok": [">", 0],
            "mevcut_stok": ["<=", frappe.db.Field("kritik_stok")]
        })
        print(f"Result of count: {count}")
    except Exception as e:
        print(f"Query failed: {e}")
