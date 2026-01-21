
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class DepoTransferi(Document):
    def validate(self):
        """
        Kayıt öncesi kontroller.
        """
        # 1. Depo Kontrolü
        if self.kaynak_depo == self.hedef_depo:
            frappe.throw("Kaynak ve Hedef depo aynı olamaz!", title="Depo Hatası")

        # 2. Stok Yeterlilik Kontrolü
        for item in self.transfer_listesi:
            # Kaynak depodaki stoğu çek
            current_qty = frappe.db.get_value("Stok Bakiyesi", 
                {"urun": item.urun, "depo": self.kaynak_depo}, 
                "mevcut_miktar"
            ) or 0.0
            
            transfer_qty = flt(item.transfer_miktari)
            
            if transfer_qty > current_qty:
                frappe.throw(
                    msg=f"Yetersiz Stok! Satır {item.idx}: '{item.urun}' ürünü için '{self.kaynak_depo}' deposunda yeterli miktar yok. (Mevcut: {current_qty}, İstenen: {transfer_qty})",
                    title="Stok Transfer Hatası"
                )

    def on_submit(self):
        """
        Onaylandığında transfer işlemini gerçekleştir.
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
        Uses shared stock_ledger.py
        
        Her satır için 2 kayıt atılır:
        1. Kaynak Depodan ÇIKIŞ
        2. Hedef Depoya GİRİŞ
        """
        from archerp.controllers.stock_ledger import create_stock_entry
        
        # İşlem Yönü Çarpanı
        action_multiplier = -1 if reverse else 1

        for item in self.transfer_listesi:
            raw_qty = flt(item.transfer_miktari)
            
            # --- KAYIT 1: KAYNAK DEPO ÇIKIŞI ---
            # Normalde Çıkış (-), Reverse ise (+)
            out_qty = (raw_qty * -1) * action_multiplier
            
            # Warehouse override needed because shared util usually looks at item.depo
            # But transfer has source/target on Header or weird structure
            # Let's mock the item dict or use kwargs if supported?
            # Our util supports 'warehouse_field' arg.
            # But here the source warehouse is on SELF (header) as 'kaynak_depo'
            # So we can pass warehouse_field="kaynak_depo" and it will look at doc.kaynak_depo if item doesn't have it.
            # BUT item DOES NOT have 'kaynak_depo' field, so it falls back to doc. PERFECT.
            
            create_stock_entry(self, item, out_qty, reverse=False, warehouse_field="kaynak_depo")
            
            
            # --- KAYIT 2: HEDEF DEPO GİRİŞİ ---
            # Normalde Giriş (+), Reverse ise (-)
            in_qty = raw_qty * action_multiplier
            
            create_stock_entry(self, item, in_qty, reverse=False, warehouse_field="hedef_depo")
