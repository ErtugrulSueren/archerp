# Copyright (c) 2026, ArcERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _


@frappe.whitelist()
def get_sidebar_menu():
    """
    Kullanıcının rollerine göre sidebar menüsünü getir.
    
    Returns:
        list: Modüller ve alt menü öğeleri
    """
    user_roles = frappe.get_roles()
    
    # Kullanıcının yetkili olduğu modülleri getir
    modules = frappe.db.sql("""
        SELECT DISTINCT 
            m.name,
            m.modul_adi,
            m.ikon,
            m.siralama
        FROM `tabArch Module` m
        LEFT JOIN `tabArch Module Role` mr ON mr.parent = m.name
        WHERE 
            m.aktif = 1
            AND (
                -- Rol tanımlı ve kullanıcı o role sahip
                mr.role IN %(roles)s
                OR
                -- Hiç rol tanımlanmamış (herkese açık)
                NOT EXISTS (
                    SELECT 1 FROM `tabArch Module Role` 
                    WHERE parent = m.name
                )
            )
        ORDER BY m.siralama ASC, m.modul_adi ASC
    """, {'roles': user_roles}, as_dict=1)
    
    # Her modülün menü öğelerini getir
    for module in modules:
        items = frappe.db.sql("""
            SELECT 
                mo.etiket,
                mo.ikon,
                mo.turu,
                mo.hedef_rota,
                mo.ilgili_doctype,
                mo.ilgili_rapor,
                mo.ust_baslik,
                mo.idx
            FROM `tabArch Menu Ogesi` mo
            WHERE 
                mo.parent = %(module)s 
                AND mo.aktif = 1
            ORDER BY mo.idx ASC, mo.etiket ASC
        """, {'module': module.name}, as_dict=1)
        
        # Gruplandırma (ust_baslik varsa)
        grouped_items = {}
        ungrouped_items = []
        
        for item in items:
            if item.ust_baslik:
                if item.ust_baslik not in grouped_items:
                    grouped_items[item.ust_baslik] = []
                grouped_items[item.ust_baslik].append(item)
            else:
                ungrouped_items.append(item)
        
        module['items'] = ungrouped_items
        module['grouped_items'] = grouped_items
    
    return modules


@frappe.whitelist()
def check_module_access(module_name):
    """
    Kullanıcının belirli bir modüle erişimi olup olmadığını kontrol et
    
    Args:
        module_name (str): Modül adı
        
    Returns:
        bool: Erişim var mı?
    """
    user_roles = frappe.get_roles()
    
    # Modülün rollerini kontrol et
    module_roles = frappe.get_all(
        'Arch Module Role',
        filters={'parent': module_name},
        fields=['role']
    )
    
    # Rol tanımlı değilse herkese açık
    if not module_roles:
        return True
    
    # Kullanıcının rolü var mı kontrol et
    allowed_roles = [r.role for r in module_roles]
    return any(role in allowed_roles for role in user_roles)
