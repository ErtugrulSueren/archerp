
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class MuhasebeDefteri(Document):
    def after_insert(self):
        """Kayıt sonrası Hesap bakiyesini güncelle"""
        self.hesap_bakiyesini_guncelle()

    def on_trash(self):
        """Silinirse etkiyi geri al"""
        self.hesap_bakiyesini_guncelle(siliniyor_mu=True)

    def hesap_bakiyesini_guncelle(self, siliniyor_mu=False):
        if not self.hesap:
            return

        # 1. Mevcut Bakiyeyi Çek
        # SQL kullanımı en güncel veriyi almak için daha güvenlidir
        mevcut_bakiye = frappe.db.get_value("Hesap", self.hesap, "guncel_bakiye") or 0.0

        # 2. Değişimi Hesapla (Borç artırır, Alacak azaltır varsayımı)
        # Not: Pasif hesaplarda normalde tam tersidir ama basit ERP'lerde B-A formülü standart tutulabilir.
        degisim = flt(self.borc) - flt(self.alacak)

        if siliniyor_mu:
            degisim = degisim * -1

        yeni_bakiye = flt(mevcut_bakiye) + degisim

        # 3. Veritabanına Yaz
        frappe.db.set_value("Hesap", self.hesap, "guncel_bakiye", yeni_bakiye)
