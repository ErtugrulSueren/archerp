
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class SatisFaturasi(Document):
    def validate(self):
        if flt(self.genel_toplam) < 0:
            frappe.throw("Genel toplam negatif olamaz.")
        if not self.vade_tarihi:
            frappe.throw("Lütfen bir Ödeme Koşulu seçiniz. Vade tarihi boş olamaz.")
        if not self.borc_hesabi:
            frappe.throw("Borç Hesabı boş olamaz.")

        # Hesapları Hazırla
        self.set_account_heads()

        # İrsaliye Miktar Kontrolü (Fazla Faturalamayı Önle)
        for item in self.kalemler:
            if item.irsaliye_kalemi_id:
                # Teslimat Kalemi'nden (DN Item) kalan miktarı çek
                # db.get_value ile 'miktar' (Sevk Edilen) ve 'faturalanan_miktar' (Billed) alıyoruz
                dn_item = frappe.db.get_value("Teslimat Kalemi", item.irsaliye_kalemi_id, ["miktar", "faturalanan_miktar"], as_dict=1)
                
                if dn_item:
                    # Kalan = Sevk Edilen - Zaten Faturalanan (Başka faturalarda)
                    # Not: Bu fatura henüz submit olmadığı için 'faturalanan_miktar'a dahil değil.
                    kalan = flt(dn_item.miktar) - flt(dn_item.faturalanan_miktar)
                    
                    # Tolerans (float hataları için)
                    if flt(item.miktar) > (kalan + 0.001):
                        frappe.throw(
                            f"Satır {item.idx}: İrsaliye miktarından fazlası faturalanamaz! <br>"
                            f"Ürün: {item.urun} <br>"
                            f"Sevk Edilen: {flt(dn_item.miktar)} <br>"
                            f"Zaten Faturalanan: {flt(dn_item.faturalanan_miktar)} <br>"
                            f"Kalan: {kalan} <br>"
                            f"Girilen: {item.miktar}"
                        )
    
    def set_account_heads(self):
         """
         Kalemler için GELİR hesaplarını set eder.
         Services -> Gelir Gider Kalemi'nden Varsayılan Hesap
         Stock -> Ürün'den Gelir Hesabı
         """
         for item in self.kalemler:
             if item.tur == "Hizmet":
                  if item.gelir_gider_kalemi and not item.muhasebe_hesabi:
                       item.muhasebe_hesabi = frappe.db.get_value("Gelir Gider Kalemi", item.gelir_gider_kalemi, "varsayilan_hesap")
             else:
                  # Stok
                  if item.urun and not item.muhasebe_hesabi:
                       item.muhasebe_hesabi = frappe.db.get_value("Urun", item.urun, "gelir_hesabi")

    # ... (On Submit and other methods remain same) ...

    def muhasebe_kaydi_olustur(self, iptal_mi=False):
        """
        KDV ve Gelir Hesaplarını Otomatik Bulan Gelişmiş Muhasebe Motoru
        1. Müşteri (Borç)
        2. Gelir Hesabı [Satır Bazlı veya Genel] (Alacak) [Net Tutar]
        3. KDV Hesabı [Vergi Şablonundan] (Alacak) [KDV Tutarı]
        """
        
        # 1. Müşteri Hesabını Bul
        musteri_hesabi = frappe.db.get_value("Musteri", self.musteri, "muhasebe_hesabi")
        
        if not musteri_hesabi:
            # Yedek: Belki formda elle seçilmiştir
            musteri_hesabi = self.borc_hesabi
            
        if not musteri_hesabi:
            frappe.throw(f"'{self.musteri_adi}' müşterisi için Muhasebe Hesabı bulunamadı. Lütfen Müşteri kartını kontrol edin.")

        # --- KAYITLARI OLUŞTUR ---

        # A. MÜŞTERİ (BORÇLU) -> Toplam Tutar
        mb_borc = self.genel_toplam if not iptal_mi else 0
        mb_alacak = 0 if not iptal_mi else self.genel_toplam
        mb_aciklama = f"Fatura Satışı: {self.name}"
        if iptal_mi: mb_aciklama = f"İPTAL: {mb_aciklama}"
        
        self.tekil_kayit_at(musteri_hesabi, mb_borc, mb_alacak, mb_aciklama, "Musteri", self.musteri)

        # B. GELİR HESABI (ALACAKLI) -> KDV Hariç Tutar (Net)
        # Satır bazlı gelir hesaplarını topla
        # { "600...": amount }
        gelir_hesaplari = {}
        
        # Genel Varsayılan Hesap (Fallback)
        default_income_account = frappe.db.get_value("Firma", self.firma, "varsayilan_gelir_hesabi")
        if not default_income_account:
             default_income_account = frappe.db.get_value("Hesap", {"hesap_kodu": "600.01"}, "name")
        
        for item in self.kalemler:
             line_net = flt(item.tutar) # Tutar zaten net (vergi hariç) olarak hesaplanmış olmalı validate/js tarafında. 
             # Wait: Fatura kalemlerinde 'tutar' fieldı genelde miktar * birim_fiyat'tır.
             # Vergi dahil mi hariç mi kontrol edelim.
             # JS/Py logic: Tutar = Miktar * Birim Fiyat. 
             # Eğer Vergi Hariç ise: Tutar = Net
             # Eğer Vergi Dahil ise: Tutar = Brüt. Net'i ayırmamız lazım.
             # Ancak `muhasebe_kaydi_olustur` öncesinde `calculate_totals` çalışmış olmalı? No, `on_submit` calls `muhasebe_kaydi_olustur`.
             # And `validate` calls `calculate_totals`? No, `validate` logic in file checks totals but doesn't recalc everything from scratch usually unless docstatus=0.
             # Let's assume `item.tutar` is (Qty * Price). Net Amount calculation required.
             
             qty = flt(item.miktar)
             price = flt(item.birim_fiyat)
             
             tax_inclusive = self.vergi_dahil_mi == 1
             tax_rate = flt(item.vergi_orani)
             
             if tax_inclusive:
                 # İçinden vergiyi ayıkla
                 net_unit_price = price / (1 + (tax_rate / 100.0))
             else:
                 net_unit_price = price
                 
             line_net_amount = qty * net_unit_price
             
             # Gelir Hesabı Seçimi
             account = item.muhasebe_hesabi or default_income_account
             
             if not account:
                  frappe.throw(f"Kalem {item.idx} için Gelir Hesabı bulunamadı. Lütfen Ürün/Hizmet kartını veya Firma varsayılanını kontrol edin.")
                  
             gelir_hesaplari[account] = gelir_hesaplari.get(account, 0) + line_net_amount

        # Gelir Hesaplarına Kayıt At
        for account, amount in gelir_hesaplari.items():
             if amount == 0: continue
             
             gh_borc = 0 if not iptal_mi else amount
             gh_alacak = amount if not iptal_mi else 0
             gh_aciklama = f"Yurtiçi Satış Geliri: {self.name}"
             if iptal_mi: gh_aciklama = f"İPTAL: {gh_aciklama}"
             
             self.tekil_kayit_at(account, gh_borc, gh_alacak, gh_aciklama, "Musteri", self.musteri)


        # C. KDV HESAPLARI (ALACAKLI) -> Vergi Şablonuna Göre
        # Satırlardaki vergi şablonlarını toparla
        # { "Vergi Templatesi Adı": { "tutar": 100, "hesap": "391.01..." } }
        vergi_toplamlari = {}
        
        for item in self.kalemler:
            if item.vergi_sablonu and item.vergi_orani > 0:
                kdv_tutari = (item.tutar * item.vergi_orani) / 100
                
                if item.vergi_sablonu not in vergi_toplamlari:
                    # Şablon detayını çek (Hesap ID'si lazım)
                    account_name = frappe.db.get_value("Vergi", item.vergi_sablonu, "muhasebe_hesabi")
                    if not account_name:
                         frappe.throw(f"'{item.vergi_sablonu}' vergi tanımında Muhasebe Hesabı seçili değil!")
                         
                    vergi_toplamlari[item.vergi_sablonu] = {
                        "hesap": account_name,
                        "tutar": 0.0
                    }
                
                vergi_toplamlari[item.vergi_sablonu]["tutar"] += kdv_tutari

        # Hesaplanan KDV'ler için kayıt at
        for sablon, detay in vergi_toplamlari.items():
            tutar = detay["tutar"]
            hesap = detay["hesap"]
            
            if tutar > 0:
                kdv_borc = 0 if not iptal_mi else tutar
                kdv_alacak = tutar if not iptal_mi else 0
                kdv_aciklama = f"Hesaplanan KDV ({sablon}): {self.name}"
                if iptal_mi: kdv_aciklama = f"İPTAL: {kdv_aciklama}"
                
                self.tekil_kayit_at(hesap, kdv_borc, kdv_alacak, kdv_aciklama, "Musteri", self.musteri)


    def tekil_kayit_at(self, hesap, borc, alacak, aciklama, muhatap_tipi=None, muhatap=None):
        gl = frappe.new_doc("Muhasebe Defteri")
        gl.tarih = self.fatura_tarihi
        gl.hesap = hesap
        gl.borc = flt(borc)
        gl.alacak = flt(alacak)
        gl.belge_tipi = "Satis Faturasi"
        gl.belge_no = self.name
        gl.aciklama = aciklama
        gl.muhatap_tipi = muhatap_tipi
        gl.carimuhatap = muhatap
        gl.insert(ignore_permissions=True)

@frappe.whitelist()
def make_payment_entry(source_name, target_doc=None):
    from frappe.model.mapper import get_mapped_doc
    from frappe.utils import flt
    
    def set_missing_values(source, target):
        target.odeme_turu = "Tahsilat(Al)"
        target.taraf_tipi = "Musteri" 
        target.taraf_kisi = source.musteri
        
        target.referans_tipi = "Satis Faturasi"
        target.referans_no = source.name
        
        # Tutar (Varsayılan olarak kalan tutarı getir)
        odenen = flt(source.odenen_tutar) if hasattr(source, 'odenen_tutar') else 0
        kalan = flt(source.genel_toplam) - odenen
        
        target.odenen_tutar = kalan if kalan > 0 else flt(source.genel_toplam)
        
    doclist = get_mapped_doc("Satis Faturasi", source_name, {
        "Satis Faturasi": {
            "doctype": "Odeme Islemi",
            "field_map": {
                "firma": "firma",
                "sube": "sube",
                "para_birimi": "para_birimi"
            }
        }
    }, target_doc, set_missing_values)

    return doclist
