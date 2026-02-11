
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, today, add_days, getdate
from archerp.controllers.transaction_controller import TransactionController

class SatisTeklifi(TransactionController):
    def validate(self):
        # 0. Hesaplamaları Çalıştır
        self.calculate_totals()

        # Toplam kontrolü
        if flt(self.genel_toplam) < 0:
             frappe.throw("Genel toplam negatif olamaz!")
             
        # Durum Kontrolü (Süresi Doldu mu?)
        if self.gercerlilik_tarihi and getdate(self.gercerlilik_tarihi) < getdate(today()) and self.status not in ["Sipariş Edildi", "İptal", "Reddedildi"]:
             self.status = "Süresi Doldu"
             
    def on_submit(self):
        # Varsayılan olarak gönderildi kabul ediyoruz
        if self.status not in ["Kabul Edildi", "Sipariş Edildi"]:
             self.db_set("status", "Müşteriye Gönderildi")

    def on_cancel(self):
        self.db_set("status", "İptal")

    def guncelle_durum(self):
        """
        Durumu günceller (Siparişten veya Süre kontrolünden çağrılabilir)
        """
        if self.docstatus == 2:
            self.db_set("status", "İptal")
            return

        # Sipariş Edildi kontrolü (Sipariş tarafından set edilirse dokunma)
        if self.status == "Sipariş Edildi":
             # Belki sipariş iptal edilmiştir? Kontrol eklenebilir.
             pass
             
        # Süre Kontrolü
        if self.gercerlilik_tarihi and getdate(self.gercerlilik_tarihi) < getdate(today()):
             cur_status = self.status
             if cur_status not in ["Sipariş Edildi", "Kabul Edildi", "İptal"]:
                  self.db_set("status", "Süresi Doldu")

@frappe.whitelist()
def make_sales_order(source_name, target_doc=None):
    """
    Satış Teklifinden Siparişe dönüştürme fonksiyonu
    """
    def set_missing_values(source, target):
        # Sipariş Tarihi = Bugün
        target.tarih = today()
        
        # Teslim Tarihi = Teklif Geçerlilik Tarihi (Yoksa Bugün + 7)
        if source.gercerlilik_tarihi:
            target.teslim_tarihi = source.gercerlilik_tarihi
        else:
            target.teslim_tarihi = add_days(today(), 7)
            
        # Kalemlerdeki eksik değerler
        for item in target.kalemler:
            item.teslim_tarihi = target.teslim_tarihi
            # Sipariş ilk oluştuğunda hepsi bekliyor
            item.kalan_miktar = item.miktar
            item.faturalanacak_miktar = item.miktar
            item.teslim_edilen_miktar = 0
            item.faturalanan_miktar = 0

        # Adres Mapping Düzeltmeleri
        # Alan İsimleri Eşitlendiği için (sevkiyat_ -> sevkiyat_) işimiz kolaylaştı.
        # Yine de Fetch From tetiklenmeme ihtimaline karşı manuel setliyoruz.
        
        # 1. Kaynakta Varsa (Öncelikli)
        if source.sevkiyat_il: target.sevkiyat_il = source.sevkiyat_il
        if source.sevkiyat_ilce: target.sevkiyat_ilce = source.sevkiyat_ilce
        if source.sevkiyat_acik_adres: target.sevkiyat_acik_adres = source.sevkiyat_acik_adres
        
        # 2. Kaynakta Yoksa ama Adres Seçiliyse (DB'den Çek)
        elif target.sevkiyat_adresi:
             addr = frappe.db.get_value("Adres Detayi", target.sevkiyat_adresi, ["sehir", "ilce", "acik_adres"], as_dict=True)
             if addr:
                 target.sevkiyat_il = addr.sehir
                 target.sevkiyat_ilce = addr.ilce
                 target.sevkiyat_acik_adres = addr.acik_adres

    doclist = get_mapped_doc("Satis Teklifi", source_name, {
        "Satis Teklifi": {
            "doctype": "Satis Siparisi",
            "field_map": {
                "musteri": "musteri",
                "para_birimi": "para_birimi",
                "doviz_kuru": "doviz_kuru",
                "firma": "firma",
                "sube": "sube",
                "fatura_adresi": "fatura_adresi",
                "sevkiyat_adresi": "sevkiyat_adresi", # Alan isimleri eşitlendi
                "odeme_kosulu": "odeme_kosulu",
                "sartlar_ve_kosullar": "sartlar_ve_kosullar",
                "fiyat_listesi": "fiyat_listesi",
                "museri_siparis_no": "museri_siparis_no", 
                "notlar": "notlar",
                "vergi_dahil_mi": "vergi_dahil_mi",
                "ek_iskonto_tutari": "ek_iskonto_tutari",
                # Adres Detayları
                "acik_adres": "fatura_acik_adres", 
                "il": "fatura_il",
                "ilce": "fatura_ilce",
                "sevkiyat_il": "sevkiyat_il",
                "sevkiyat_ilce": "sevkiyat_ilce",
                "sevkiyat_acik_adres": "sevkiyat_acik_adres"
            }
        },
        "Satis Kalemi": {
            "doctype": "Siparis Kalemi",
            "field_map": {
                "urun": "urun",
                "urun_adi": "urun_adi",
                "miktar": "miktar",
                "birim_fiyat": "birim_fiyat",
                "stok_birimi": "stok_birimi",
                "cevrim_katsayisi": "cevrim_katsayisi",
                "depo": "depo",
                "iskonto_orani": "iskonto_orani",
                "iskonto_tutari": "iskonto_tutari",
                "vergi_sablonu": "vergi_sablonu",
                "vergi_orani": "vergi_orani",
                "tutar": "tutar"
            }
        }
    }, target_doc, set_missing_values)

    return doclist
