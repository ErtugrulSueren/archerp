
import frappe

@frappe.whitelist(allow_guest=True)
def get_sidebar_menu():
    """
    Frontend için sol menü ağacını getirir.
    Arch Module -> Arch Menu Ogesi yapısını JSON olarak döner.
    """
    menu_tree = []
    
    # 1. Aktif modülleri sıralı şekilde çek
    modules = frappe.get_all("Arch Module", 
                             filters={"aktif": 1}, 
                             order_by="siralama asc", 
                             fields=["name"])

    for mod in modules:
        # Modülün detaylarını ve child table'ını (menu_ogeleri) yükle
        mod_doc = frappe.get_doc("Arch Module", mod.name)
        
        module_data = {
            "category": mod_doc.modul_adi,
            "icon": mod_doc.ikon,
            "items": []
        }

        # Child table'daki aktif öğeleri ekle
        for item in mod_doc.menu_ogeleri:
            if item.aktif:
                menu_item = {
                    "etiket": item.etiket,
                    "ikon": item.ikon,
                    "turu": item.turu,
                    "hedef_rota": item.hedef_rota,
                    "ilgili_doctype": item.ilgili_doctype,
                    "ilgili_rapor": item.ilgili_rapor,
                    "ust_baslik": item.ust_baslik
                }
                module_data["items"].append(menu_item)

        # Eğer modülün altında hiç aktif öğe yoksa menüde gösterme (Opsiyonel, temizlik için iyi)
        if module_data["items"]:
            menu_tree.append(module_data)

    return menu_tree

@frappe.whitelist(allow_guest=True)
def debug_vergi():
    return frappe.get_all("Vergi", fields=["name", "vergi_turu", "is_default"])


