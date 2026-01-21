# Copyright (c) 2025, Ertu and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class StokDefteri(Document):
    def validate(self):
        """
        Kayıt öncesi kontroller.
        """
        # Stok Düşümü Kontrolü (Negatif Stok Engelleme)
        if self.degisim_miktari < 0:
            # İlgili depodaki mevcut bakiyeyi bul
            bin_filters = {"urun": self.urun, "depo": self.depo}
            
            # Bakiyeyi çek
            existing_qty = frappe.db.get_value("Stok Bakiyesi", bin_filters, "mevcut_miktar") or 0
            
            # Gelecek bakiye tahmini
            future_qty = existing_qty + self.degisim_miktari
            
            if future_qty < 0:
                frappe.throw(
                    msg=f"Yetersiz Stok! '{self.depo}' deposunda '{self.urun}' ürünü için yeterli miktar yok.<br>Mevcut: {existing_qty}, Çıkılmak İstenen: {abs(self.degisim_miktari)}",
                    title="Negatif Stok Hatası"
                )

    def after_insert(self):
        """
        Stok kaydı girildiğinde ilgili Depo ve Ürün için Bakiyeyi güncelle.
        Zincir: Stok Defteri -> Stok Bakiyesi (Bin) -> Ürün (Item)
        """
        if not self.urun or not self.depo or not self.degisim_miktari:
            return

        # 1. Mevcut Bakiyeyi Bul veya Oluştur
        # ID Formatımız artık kesin: {URUN}-{DEPO} (Stok Bakiyesi autoname hallediyor)
        # Oluşacak veya aranacak ID:
        bin_id = f"{self.urun}-{self.depo}".replace(" ", "-")
        
        # Direkt ID ile dene
        if frappe.db.exists("Stok Bakiyesi", bin_id):
            bin_doc = frappe.get_doc("Stok Bakiyesi", bin_id)
        else:
            # Bulamazsan ikincil kontrol (Filtre ile)
            # Eğer eski formatta (hash) kayıt varsa onu bulsun, yoksa yenisini oluşturacağız.
            filters = {"urun": self.urun, "depo": self.depo}
            if frappe.db.exists("Stok Bakiyesi", filters):
                 existing_name = frappe.db.get_value("Stok Bakiyesi", filters, "name")
                 bin_doc = frappe.get_doc("Stok Bakiyesi", existing_name)
            else:
                # Hiç yok, Yeni Oluştur
                bin_doc = frappe.new_doc("Stok Bakiyesi")
                bin_doc.urun = self.urun
                bin_doc.depo = self.depo
                bin_doc.mevcut_miktar = 0
                bin_doc.degerleme_tutari = 0.0 # Yeni alan
                # name set etmeye gerek yok, autoname() halledecek.
            
        # 2. Alanları Güncelle
        # Birimi Taşı (Sorgusuz Veri Akışı)
        if self.birim:
            bin_doc.stok_birimi = self.birim 
        
        # Miktarı Güncelle
        current_qty = flt(bin_doc.mevcut_miktar)
        bin_doc.mevcut_miktar = current_qty + flt(self.degisim_miktari)
        
        # Maliyet (Değerleme) Güncelleme
        # Değişim Tutarı = Giriş/Çıkış Miktarı * Birim Maliyet
        unit_cost = flt(self.birim_maliyet)
        total_change_val = flt(self.degisim_miktari) * unit_cost
        
        current_val = flt(bin_doc.degerleme_tutari)
        bin_doc.degerleme_tutari = current_val + total_change_val
        
        # Eksiye düşerse (ki olmamalı normalde ama güvenlik) 0 yap
        if bin_doc.degerleme_tutari < 0 and bin_doc.mevcut_miktar <= 0:
             bin_doc.degerleme_tutari = 0.0

        # Ortalama Maliyet Hesapla
        # Formül: Toplam Değer / Toplam Miktar
        if bin_doc.mevcut_miktar > 0:
            bin_doc.birim_maliyet = bin_doc.degerleme_tutari / bin_doc.mevcut_miktar
        else:
            # Stok sıfırlandıysa veya eksiye düştüyse maliyeti sıfırla (veya son maliyet tutulabilir, şimdilik 0)
            bin_doc.birim_maliyet = 0.0
        
        # 3. Kaydet
        # Eğer yeni ise insert (autoname çalışsın diye), eski ise save.
        if bin_doc.is_new():
            bin_doc.insert(ignore_permissions=True)
        else:
            bin_doc.save(ignore_permissions=True)
        
        frappe.msgprint(f"Bilgi: {self.depo} deposundaki stok bakiyesi güncellendi.")
