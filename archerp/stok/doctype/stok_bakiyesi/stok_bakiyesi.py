# Copyright (c) 2025, Ertu and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class StokBakiyesi(Document):
    def autoname(self):
        """
        ID Formatını Zorla: {URUN}-{DEPO}
        Örn: A4-KAGIT-ANA-DEPO
        """
        self.name = f"{self.urun}-{self.depo}".replace(" ", "-")

    def validate(self):
        """
        Validasyon Kuralları
        """
        # Benzersizlik Kontrolü: Aynı Ürün ve Depo için ikinci bir kart olamaz
        if self.is_new():
            existing = frappe.db.exists("Stok Bakiyesi", {
                "urun": self.urun,
                "depo": self.depo
            })
            if existing:
                frappe.throw(
                    msg=f"Bu Ürün ({self.urun}) ve Depo ({self.depo}) için zaten bir Stok Bakiyesi kaydı mevcut.",
                    title="Mükerrer Kayıt Hatası"
                )

    def on_update(self):
        """
        Stok Bakiyesi (Bin) güncellendiğinde, bağlı olduğu Ürün (Item) kartını güncelle.
        Mantık: Bir ürünün farklı depolardaki bakiye toplamı = Ürün Ana Kartı Stoğu
        """
        if not self.urun:
            return

        # 1. Bu ürün için tüm bakiyeleri topla
        total_balance = frappe.db.sql("""
            SELECT SUM(mevcut_miktar)
            FROM `tabStok Bakiyesi`
            WHERE urun = %s
        """, (self.urun,))

        current_total = flt(total_balance[0][0]) if total_balance and total_balance[0][0] else 0.0

        # 2. Ürün kartını güncelle
        # db.set_value sanal alanlara yazmaz, alanın gerçek olduğundan emin olundusu
        frappe.db.set_value("Urun", self.urun, "mevcut_stok", current_total)
