# Copyright (c) 2025, Ertu and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SartlarveKosullar(Document):
    def before_save(self):
        """
        Tekil Varsayılan Kontrolü:
        Eğer bu kayıt varsayılan (is_default=1) yapılıyorsa,
        sistemdeki diğer tüm varsayılanların işareti kaldırılır.
        """
        if self.is_default == 1 or self.is_default == "1":
            # Sistemdeki diğer varsayılan kayıtları bul (Kendisi hariç)
            other_defaults = frappe.get_all("Sartlar ve Kosullar", filters={
                "is_default": 1,
                "name": ["!=", self.name]
            })

            # Diğerlerinin is_default değerini 0 yap
            for other in other_defaults:
                frappe.db.set_value("Sartlar ve Kosullar", other.name, "is_default", 0)
                frappe.msgprint(f"Bilgi: '{other.name}' kaydının varsayılan özelliği kaldırıldı.")
