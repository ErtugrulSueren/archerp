import frappe
from archerp.controllers.transaction_controller import TransactionController
from frappe.utils import flt

class SatinAlmaFaturasi(TransactionController):
    def validate(self):
        super().validate()
        # Add any specific validation here

    def on_submit(self):
        self.mal_kabul_guncelle()
        self.siparis_guncelle()
        self.make_gl_entries()
        
    def on_cancel(self):
        self.mal_kabul_guncelle()
        self.siparis_guncelle()
        self.make_gl_entries(cancel=True)

    def make_gl_entries(self, cancel=False):
        # 1. Tedarikçi Hesabı (Alacak)
        tedarikci_hesabi = frappe.db.get_value("Tedarikci", self.tedarikci, "muhasebe_hesabi")
        if not tedarikci_hesabi:
             frappe.throw(f"Tedarikçi {self.tedarikci} için Muhasebe Hesabı tanımlanmamış!")

        # 2. Kalem Gider Hesapları ve Vergiler (Borç)
        # Vergileri hesap bazında topla
        tax_entries = {} # {account: amount}
        
        tax_inclusive = self.vergi_dahil_mi == 1
        
        # Firma Ayarları (Stok kalemleri için SRBNB hesabı)
        srbnb_account = frappe.db.get_value("Firma", self.firma, "mal_kabul_hesabi")
        
        for item in self.kalemler:
            # Hesaplama (Tekrar) necessary for GL accuracy or rely on stored values?
            # It relies on stored values usually. 
            # But here it recalculates to be safe or uses fields.
            # Using fields is safer if validate ran.
            
            qty = flt(item.miktar)
            line_net = flt(item.tutar) # Already calculated by validate
            
            # Recalculate tax just to be sure about the split? 
            # Or use stored tax amounts if we had them per line?
            # The original code recalculated. Let's keep recalculation for safety or reuse simple logic.
            # Actually, calculate_totals stores 'total_tax' but not per-line tax split in child table usually unless field exists.
            # ArchERP doesn't seem to have 'vergi_tutari' field in child table in previous code.
            # So we must recalculate tax here to know map to account.
            
            price = flt(item.birim_fiyat)
            tax_rate = flt(item.vergi_orani)
            
            if tax_inclusive:
                net_unit_price = price / (1 + (tax_rate / 100.0))
                unit_tax = price - net_unit_price
            else:
                net_unit_price = price
                unit_tax = net_unit_price * (tax_rate / 100.0)
                
            line_tax = qty * unit_tax
            
            # DEBIT ACCOUNT SELECTION
            debit_account = None
            
            if item.tur == "Hizmet":
                 # Hizmet Kalemi -> Gider Hesabı (muhasebe_hesabi)
                 if not item.muhasebe_hesabi:
                      frappe.throw(f"Hizmet kalemi {item.idx} için Muhasebe Hesabı bulunamadı!")
                 debit_account = item.muhasebe_hesabi
            else:
                 # Stok Kalemi -> SRBNB (Mal Kabul Hesabı)
                 if not srbnb_account:
                      frappe.throw("Firma ayarlarında 'Mal Kabul Hesabı' (SRBNB) tanımlı değil!")
                 debit_account = srbnb_account
            
            # Use Parent create_gl_entry
            self.create_gl_entry(debit_account, line_net, 0, cancel, party_type="Tedarikci", party=self.tedarikci)
            
            # Vergi Hesabını Bul ve Topla
            if line_tax > 0 and item.vergi_sablonu:
                 vergi_hesabi = frappe.db.get_value("Vergi", item.vergi_sablonu, "muhasebe_hesabi")
                 if vergi_hesabi:
                      tax_entries[vergi_hesabi] = tax_entries.get(vergi_hesabi, 0) + line_tax

        # Vergi Kayıtlarını Oluştur
        for account, amount in tax_entries.items():
             self.create_gl_entry(account, amount, 0, cancel, party_type="Tedarikci", party=self.tedarikci)
             
        # Tedarikçi Alacak Kaydı (Toplam)
        self.create_gl_entry(tedarikci_hesabi, 0, self.genel_toplam, cancel, party_type="Tedarikci", party=self.tedarikci)

    def mal_kabul_guncelle(self):
        """
        Bağlı Mal Kabul Fişi varsa, onun faturalanan miktarlarını günceller.
        """
        if self.ilgili_mal_kabul:
            mk = frappe.get_doc("Mal Kabul Fisi", self.ilgili_mal_kabul)
            mk.fatura_guncelle()
            
    def siparis_guncelle(self):
        """
        Bağlı Satin Alma Siparisi varsa (direkt fatura), onun faturalanan miktarlarını günceller.
        """
        if self.satin_alma_siparisi_referansi:
             siparis = frappe.get_doc("Satin Alma Siparisi", self.satin_alma_siparisi_referansi)
             siparis.guncelle_faturalanan()

@frappe.whitelist()
def make_payment_entry(source_name, target_doc=None):
    from frappe.model.mapper import get_mapped_doc
    
    def set_missing_values(source, target):
        target.odeme_turu = "Tediye(Ver)"
        target.taraf_tipi = "Tedarikci" 
        target.taraf_kisi = source.tedarikci
        # Odeme Yontemi varsayılan olarak seçili gelmeyebilir, kullanıcı seçer.
        
        target.referans_tipi = "Satin Alma Faturasi"
        target.referans_no = source.name
        
        # Tutar (Varsayılan olarak kalan tutarı getir)
        odenen = flt(source.odenen_tutar) if hasattr(source, 'odenen_tutar') else 0
        kalan = flt(source.genel_toplam) - odenen
        
        target.odenen_tutar = kalan if kalan > 0 else flt(source.genel_toplam)
        
    doclist = get_mapped_doc("Satin Alma Faturasi", source_name, {
        "Satin Alma Faturasi": {
            "doctype": "Odeme Islemi",
            "field_map": {
                # Maplenecek ortak alanlar varsa
            }
        }
    }, target_doc, set_missing_values)

    return doclist
