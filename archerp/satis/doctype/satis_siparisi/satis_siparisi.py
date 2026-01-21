
import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, today
from frappe.model.mapper import get_mapped_doc

class SatisSiparisi(Document):
    def validate(self):
        # 1. Zorunlu Alan Kontrolü (Fatura Açık Adres)
        if not self.fatura_acik_adres:
             frappe.throw("Fatura kesebilmek için 'Fatura Açık Adres' bilgisi zorunludur.")

        # 2. Negatif Toplam Kontrolü
        if flt(self.genel_toplam) < 0:
             frappe.throw("Genel toplam negatif olamaz!")

        # 3. Tarih Kontrolü
        if self.tarih and self.teslim_tarihi:
            if getdate(self.teslim_tarihi) < getdate(self.tarih):
                frappe.throw("Teslim tarihi, sipariş tarihinden önce olamaz!")

        # 4. Teklif Kontrolü
        if self.teklif_referansi:
             offer_status = frappe.db.get_value("Satis Teklifi", self.teklif_referansi, "status")
             if offer_status in ["İptal", "Reddedildi", "Süresi Doldu", "Sipariş Edildi"]:
                  # Not: Zaten sipariş edilmişse tekrar siparişe izin vermeli miyiz?
                  # Genelde hayır, yeni sipariş yeni teklif veya revize gerekir.
                  # Ancak "Kısmi Sipariş" varsa durum "Kısmi Sipariş Edildi" olmalıydı.
                  # Şimdilik bloklayalım.
                  frappe.throw(f"Seçilen teklifin durumu uygun değil: {offer_status}")
    
    def on_submit(self):
        self.teklif_durum_guncelle("Sipariş Edildi")
        self.guncelle_durum()

    def on_cancel(self):
        self.teklif_durum_guncelle("Müşteriye Gönderildi") # Eski haline döndür
        self.guncelle_durum()

    def teklif_durum_guncelle(self, status):
        if self.teklif_referansi:
             frappe.db.set_value("Satis Teklifi", self.teklif_referansi, "status", status)

    def guncelle_teslim_edilen(self):
        """
        Siparis kalemlerinin teslim edilen miktarlarını günceller ve durumu set eder.
        Sevk İrsaliyesi submit/cancel olduğunda çağrılır.
        """
        # Burada basitçe irsaliyelerden yeniden toplayabiliriz veya delta yapabiliriz.
        # Güvenli olan yeniden hesaplamaktır (re-calculation).
        
        # Sıfırla
        for item in self.kalemler:
            item.teslim_edilen_miktar = 0.0
            
        # İrsaliyelerden Bul
        # Teslimat Kalemi -> satis_kalemi_id (link to Siparis Kalemi name)
        # Parent (Sevk Irsaliyesi) submitted olmalı.
        
        irsaliye_kalemleri = frappe.db.sql("""
            SELECT tk.satis_kalemi_id, SUM(tk.miktar) as sevk_miktar
            FROM `tabTeslimat Kalemi` tk
            JOIN `tabSevk Irsaliyesi` su ON tk.parent = su.name
            WHERE su.docstatus = 1 AND tk.satis_kalemi_id IN (
                SELECT name FROM `tabSiparis Kalemi` WHERE parent = %s
            )
            GROUP BY tk.satis_kalemi_id
        """, (self.name), as_dict=True)
        
        for row in irsaliye_kalemleri:
            for item in self.kalemler:
                if item.name == row.satis_kalemi_id:
                    item.teslim_edilen_miktar = flt(row.sevk_miktar)
                    
        self.save(ignore_permissions=True)
        self.guncelle_durum()

    def guncelle_faturalanan(self):
        """
        Siparis kalemlerinin faturalanan miktarlarını günceller.
        Satis Faturasi submit/cancel olduğunda çağrılır.
        """
        # Sıfırla
        for item in self.kalemler:
            item.faturalanan_miktar = 0.0
            
        fatura_kalemleri = frappe.db.sql("""
            SELECT fk.satis_kalemi_id, SUM(fk.miktar) as fatura_miktar
            FROM `tabFatura Kalemi` fk
            JOIN `tabSatis Faturasi` sf ON fk.parent = sf.name
            WHERE sf.docstatus = 1 AND fk.satis_kalemi_id IN (
                SELECT name FROM `tabSiparis Kalemi` WHERE parent = %s
            )
            GROUP BY fk.satis_kalemi_id
        """, (self.name), as_dict=True)
        
        for row in fatura_kalemleri:
            for item in self.kalemler:
                if item.name == row.satis_kalemi_id:
                    item.faturalanan_miktar = flt(row.fatura_miktar)
        
        self.save(ignore_permissions=True)
        self.guncelle_durum()

    def guncelle_durum(self):
        if self.docstatus != 1:
            return

        toplam_miktar = 0
        toplam_teslim = 0
        toplam_fatura = 0

        for item in self.kalemler:
            toplam_miktar += flt(item.miktar)
            toplam_teslim += flt(item.teslim_edilen_miktar)
            toplam_fatura += flt(item.faturalanan_miktar)

        status = "Onay Bekliyor" # Varsayılan (Submit sonrası)
        
        # Mantık Önceliği
        # 1. Tamamlandı: Hepsi teslim + Hepsi fatura (Veya faturalama zorunluluğu yoksa Teslim bitince?)
        # Genelde Tamamlandı = Teslimat TAM + Fatura TAM
        
        if toplam_teslim >= toplam_miktar and toplam_fatura >= toplam_miktar:
            status = "Tamamlandı"
        elif toplam_teslim >= toplam_miktar:
            # Teslimat bitti, fatura eksik
            status = "Faturalanacak"
        elif toplam_fatura > 0:
            # Faturalama başladı ama teslimat bitmedi (veya fatura da bitmedi)
            status = "Kısmi Faturalandı"
        elif toplam_teslim > 0:
             # Teslimat başladı, fatura yok
             status = "Kısmi Teslimat"
        else:
             # Hiç işlem yok
             status = "Teslim Edilecek"
             
        self.db_set('status', status)

@frappe.whitelist()
def make_delivery_note(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.tarih = today()
        
        # 1. Fatura Adresini Her Zaman Aktar
        target.fatura_adresi = source.fatura_adresi
        target.fatura_il = source.fatura_il
        target.fatura_ilce = source.fatura_ilce
        target.fatura_acik_adres = source.fatura_acik_adres
        
        # 2. Sevkiyat Adresi Mantığı (Fallback)
        if source.sevkiyat_adresi:
            target.sevk_adresi = source.sevkiyat_adresi
            target.sevkiyat_il = source.sevkiyat_il
            target.sevkiyat_ilce = source.sevkiyat_ilce
            target.sevkiyat_acik_adres = source.sevkiyat_acik_adres
        else:
            target.sevk_adresi = source.fatura_adresi
            target.sevkiyat_il = source.fatura_il
            target.sevkiyat_ilce = source.fatura_ilce
            target.sevkiyat_acik_adres = source.fatura_acik_adres

        # 3. Kısmi Teslimat Mantığı
        items_to_remove = []
        for item in target.kalemler:
             source_item_id = item.satis_kalemi_id
             if source_item_id:
                  source_item = next((i for i in source.kalemler if i.name == source_item_id), None)
                  if source_item:
                       # Kalan = Sipariş Miktarı - Teslim Edilen
                       remaining_qty = flt(source_item.miktar) - flt(source_item.teslim_edilen_miktar)
                       
                       if remaining_qty <= 0:
                            items_to_remove.append(item)
                       else:
                            item.miktar = remaining_qty
        
        for item in items_to_remove:
             target.kalemler.remove(item)
             
        if not target.kalemler:
             frappe.throw("Bu siparişin tüm ürünleri zaten sevk edilmiş!")

        # 4. Tutarları Yeniden Hesapla
        target.genel_toplam = 0 # Sıfırla
        # Sevk İrsaliyesi genellikle tutar göstermez ama altyapıda olabilir/istenirse.
        # İrsaliye validate'inde genel_toplam kontrolü var, o yüzden hesaplasak iyi olur.
        # Ancak irsaliye kalemi genellikle tutar alanı içermez (fatura kalemi içerir).
        # JSON kontrolü: Teslimat Kalemi'nde 'tutar' var.
        
        target.genel_toplam = 0 
        
        # Basitçe satır tutarlarını topla (eğer fiyat varsa)
        toplam_tutar = 0
        for item in target.kalemler:
            if item.birim_fiyat:
                item_tutar = flt(item.miktar) * flt(item.birim_fiyat)
                toplam_tutar += item_tutar
                # item.tutar = item_tutar # DocType'da varsa
        
        target.genel_toplam = toplam_tutar

    doclist = get_mapped_doc("Satis Siparisi", source_name, {
        "Satis Siparisi": {
            "doctype": "Sevk Irsaliyesi",
            "field_map": {
                "name": "siparis_referansi",
                "musteri": "musteri",
                "firma": "firma",
                "sube": "sube",
                "para_birimi": "para_birimi",
                "doviz_kuru": "doviz_kuru",
                "vergi_dahil_mi": "vergi_dahil_mi",
                "ek_iskonto_tutari": "ek_iskonto_tutari",
                "notlar": "notlar",
                "odeme_kosulu": "odeme_kosulu",
                "sartlar_ve_kosullar": "sartlar_ve_kosullar"
            }
        },
        "Siparis Kalemi": {
            "doctype": "Teslimat Kalemi",
            "field_map": {
                "name": "satis_kalemi_id",
                "urun": "urun",
                "urun_adi": "urun_adi",
                "miktar": "miktar",
                "birim_fiyat": "birim_fiyat",
                "stok_birimi": "stok_birimi",
                "depo": "depo",
                "vergi_sablonu": "vergi_sablonu",
                "vergi_orani": "vergi_orani"
            }
        }
    }, target_doc, set_missing_values)

    return doclist

