# Copyright (c) 2025, Ertu and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Vergi(Document):
    def before_save(self):
        """
        Varsayılan vergi mantığı:
        Eğer bu kayıt 'Varsayılan' (is_default=1) yapılıyorsa,
        aynı 'tur'deki diğer kayıtların varsayılan özelliğini kaldır.
        """
        if self.is_default == 1 or self.is_default == "1":
            # Aynı türdeki (Satış/Alış) diğer varsayılan kayıtları bul
            other_defaults = frappe.get_all("Vergi", filters={
                "vergi_turu": self.vergi_turu,
                "is_default": 1,
                "name": ["!=", self.name]
            })

            # Diğerlerinin is_default değerini 0 yap
            for other in other_defaults:
                frappe.db.set_value("Vergi", other.name, "is_default", 0)
                frappe.msgprint(f"Bilgi: '{other.name}' vergisinin varsayılan özelliği kaldırıldı.")
