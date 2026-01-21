
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class StokDuzenlemeFisi(Document):
    def validate(self):
        """
        Kayıt öncesi kontroller.
        """
        if not self.fark_hesabi:
             frappe.throw("Lütfen farkların yansıtılacağı 'Fark Hesabı'nı seçiniz.", title="Eksik Bilgi")

    def on_submit(self):
        """
        Onaylandığında stok eşitleme işlemini gerçekleştir.
        """
        self.make_stock_entry(reverse=False)

    def on_cancel(self):
        """
        İptal edildiğinde işlemi geri al.
        """
        self.make_stock_entry(reverse=True)

    def make_stock_entry(self, reverse=False):
        """
        Stok Defteri kaydı oluşturur.
        Hareket: Fark Miktarı kadar giriş veya çıkış yapılır.
        Uses shared stock_ledger.py
        """
        from archerp.controllers.stock_ledger import create_stock_entry
        
        action_multiplier = -1 if reverse else 1

        for item in self.kalemler:
            fark = flt(item.fark_miktari)
            
            # Fark 0 ise işlem yapmaya gerek yok
            if fark == 0:
                continue
            
            # --- Değişim Hesabı ---
            # Eğer Fark -2 ise: Stoktan 2 çıkmalı. (Change = -2)
            # Eğer Fark +5 ise: Stoğa 5 girmeli. (Change = +5)
            # İptal durumunda bu işaret tersine döner.
            
            change = fark * action_multiplier
            
            # Warehouse Logic: item has NO warehouse field, parent has 'depo'.
            create_stock_entry(self, item, change, reverse=False, warehouse_field="depo")
