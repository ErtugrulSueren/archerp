
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe.model.mapper import get_mapped_doc

class SevkIrsaliyesi(Document):
    def validate(self):
        """
        Kayıt öncesi doğrulama.
        """
        if flt(self.genel_toplam) < 0:
            frappe.throw("Genel toplam negatif olamaz!")

        if not self.sevkiyat_acik_adres:
             frappe.throw("Sevk Adresi (Açık Adres) boş olamaz. Lütfen adres seçin veya girin.")

        # Hesapları Hazırla
        self.set_account_heads()

        # İade değilse (Normal Satış) stok kontrolü zorunlu
        if not self.iade_mi:
            self.check_stock_availability()
            
    def set_account_heads(self):
         """
         Kalemler için muhasebe hesaplarını set eder.
         Services -> Gelir Gider Kalemi'nden (Kullanılmasa da dursun)
         Stock -> Ürün'den Gider Hesabı (SMM/COGS)
         """
         for item in self.kalemler:
             if item.tur == "Hizmet":
                  if item.gelir_gider_kalemi and not item.muhasebe_hesabi:
                       item.muhasebe_hesabi = frappe.db.get_value("Gelir Gider Kalemi", item.gelir_gider_kalemi, "varsayilan_hesap")
             else:
                  # Stok
                  if item.urun and not item.muhasebe_hesabi:
                       item.muhasebe_hesabi = frappe.db.get_value("Urun", item.urun, "gider_hesabi")

    def check_stock_availability(self):
        for item in self.kalemler:
            if item.tur == "Hizmet": continue # Hizmet için stok bakılmaz
            
            if not item.depo:
                frappe.throw(f"Satır {item.idx}: Depo seçilmedi!")

            # Depodaki stoğu sorgula
            current_qty = frappe.db.get_value("Stok Bakiyesi", 
                {"urun": item.urun, "depo": item.depo}, 
                "mevcut_miktar"
            ) or 0.0
            
            required_qty = flt(item.miktar)
            
            if required_qty > current_qty:
                frappe.throw(
                    msg=f"Yetersiz Stok! Satır {item.idx}: '{item.urun}' ürünü için '{item.depo}' deposunda yeterli miktar yok. (Mevcut: {current_qty}, İstenen: {required_qty})",
                    title="Stok Hatası"
                )

    def on_submit(self):
        """
        Stoktan düş veya stoğa al (İade).
        """
        self.make_stock_entry(reverse=False)
        self.make_gl_entries(cancel=False)
        self.guncelle_durum()
        self.siparis_guncelle()

    def on_cancel(self):
        self.make_stock_entry(reverse=True)
        self.make_gl_entries(cancel=True)
        self.guncelle_durum()
        self.siparis_guncelle()

    def make_gl_entries(self, cancel=False):
        """
        Sürekli Envanter (Perpetual Inventory) - SMM Kayıtları
        """
        company_settings = frappe.db.get_value("Firma", self.firma, 
            ["smm_hesabi", "varsayilan_stok_hesabi"], as_dict=True)
            
        default_cogs_account = company_settings.smm_hesabi
        default_stock_account = company_settings.varsayilan_stok_hesabi
        
        # Eğer firma genel SMM hesabı yoksa ve satırlarda da özel yoksa sorun çıkabilir.
        # Şimdilik devam edelim.

        is_return = self.iade_mi
        
        for item in self.kalemler:
             # Hizmet Kalemleri: Stok maliyeti olmadığı için SMM kaydı atılmaz.
             if item.tur == "Hizmet":
                  continue
        
             # Maliyet Tutarı
             # make_stock_entry içinde hesaplanan birim maliyeti kullanabiliriz ama orası local scope.
             # Yeniden hesaplayalım.
             qty = flt(item.miktar)
             unit_cost = flt(item.birim_maliyet)
             if unit_cost == 0:
                  unit_cost = flt(frappe.db.get_value("Urun", item.urun, "standart_maliyet"))
             
             cost_amount = qty * unit_cost
             if cost_amount == 0: continue
             
             # Stok Hesabı
             warehouse_account = frappe.db.get_value("Depo", item.depo, "stok_hesabi")
             stock_account = warehouse_account or default_stock_account
             
             if not stock_account:
                   frappe.throw(f"'{item.depo}' deposu için Stok Hesabı tanımlı değil!")
                   
             # SMM/COGS Hesabı Seçimi
             # Önce satırdaki 'muhasebe_hesabi' (Ürün Gider Hesabı), yoksa Firma SMM
             cogs_account = item.muhasebe_hesabi or default_cogs_account
             
             if not cogs_account:
                  # SMM hesabı bulunamazsa, kaydı atma (veya hata ver)
                  # Hata vermek daha güvenli
                   frappe.throw(f"Kalem {item.idx} ({item.urun}) için SMM (Gider) Hesabı bulunamadı. Lütfen Ürün kartında veya Firma ayarlarında tanımlayın.")
                   
             # Normal Satış:
             # Borç: SMM (Gider)
             # Alacak: Stok (Varlık)
             
             if not is_return:
                  debit_account = cogs_account
                  credit_account = stock_account
             else:
                  # Satış İadesi:
                  # Borç: Stok
                  # Alacak: SMM
                  debit_account = stock_account
                  credit_account = cogs_account
                  
             # DEBIT
             self.create_gl_entry(debit_account, cost_amount, 0, cancel, "Musteri", self.musteri)
             
             # CREDIT
             self.create_gl_entry(credit_account, 0, cost_amount, cancel, "Musteri", self.musteri)

    def create_gl_entry(self, account, debit, credit, cancel, party_type=None, party=None):
        if debit == 0 and credit == 0: return

        gl = frappe.new_doc("Muhasebe Defteri")
        gl.belge_tipi = "Sevk Irsaliyesi"
        gl.belge_no = self.name
        gl.tarih = self.tarih
        gl.hesap = account
        gl.aciklama = f"Sevkiyat Maliyeti: {self.name} - {self.musteri}"
        gl.muhatap_tipi = party_type
        gl.carimuhatap = party
        if self.firma:
            gl.firma = self.firma
        if self.sube:
            gl.sube = self.sube
        
        if cancel:
             gl.borc = credit
             gl.alacak = debit
        else:
             gl.borc = debit
             gl.alacak = credit
             
        gl.insert(ignore_permissions=True)

    def siparis_guncelle(self):
        """
        Bağlı satış siparişini güncelle.
        """
        siparisler = set()
        
        # 1. Header'dan
        if self.siparis_referansi:
             siparisler.add(self.siparis_referansi)
             
        # 2. Kalemlerden
        for item in self.kalemler:
             if item.satis_kalemi_id:
                  sip_name = frappe.db.get_value("Siparis Kalemi", item.satis_kalemi_id, "parent")
                  if sip_name:
                       siparisler.add(sip_name)
                 
        for sip_name in siparisler:
             if frappe.db.exists("Satis Siparisi", sip_name):
                 sip = frappe.get_doc("Satis Siparisi", sip_name)
                 if hasattr(sip, "guncelle_teslim_edilen"):
                     sip.guncelle_teslim_edilen()

    def guncelle_durum(self):
        """
        İrsaliyenin faturalanma durumunu günceller.
        """
        if self.docstatus != 1:
            return

        toplam_miktar = 0
        faturalanan_miktar = 0

        for item in self.kalemler:
            toplam_miktar += flt(item.miktar)
            faturalanan_miktar += flt(item.faturalanan_miktar)

        status = "Faturalanacak"
        
        if faturalanan_miktar <= 0:
            status = "Faturalanacak"
        elif faturalanan_miktar < toplam_miktar:
            status = "Kısmi Faturalandı"
        else:
            status = "Tamamlandı"

        self.db_set('status', status)

    def make_stock_entry(self, reverse=False):
        """
        Stok Defteri kaydı oluşturur.
        Uses shared stock_ledger.py
        """
        from archerp.controllers.stock_ledger import create_stock_entry
        
        # Temel yön (Satışsa Eksi, İadeyse Artı)
        is_return = self.iade_mi
        
        # Miktar Çarpanı
        # Satış = Çıkış (-), İade = Giriş (+)
        direction = 1 if is_return else -1
        
        for item in self.kalemler:
            # Hizmet kontrolü stock_controller'a da taşınabilir ama burada filter yapmak daha güvenli
            if item.tur == "Hizmet": continue
            
            raw_qty = flt(item.miktar)
            signed_qty = raw_qty * direction
            
            create_stock_entry(self, item, signed_qty, reverse=reverse, warehouse_field="depo")

@frappe.whitelist()
def make_sales_invoice(source_name, target_doc=None):
    def set_missing_values(source, target):
        # 1. Stok Güncellemeyi Kapat (Çünkü İrsaliyede yapıldı)
        target.stok_guncelle = 0
        
        # 2. Borç Hesabını Bul (Varsayılan)
        if not target.borc_hesabi:
             default_account = frappe.db.get_value("Hesap", {"hesap_adi": "Muhtelif Alıcılar"}, "name")
             if default_account:
                  target.borc_hesabi = default_account
        
        # 3. Satırlar için Gelir Hesabı
        income_account = frappe.db.get_value("Hesap", {"hesap_adi": "Yurtiçi Satışlar"}, "name")
        
        items_to_remove = []
        for item in target.kalemler:
             # Gelir Hesabı
             if not item.gelir_hesabi and income_account:
                  item.gelir_hesabi = income_account
             
             # Kısmi Faturalama Mantığı
             # Kaynak satırı bul (irsaliye_kalemi_id mapper'dan gelir)
             source_item_id = item.irsaliye_kalemi_id
             if source_item_id:
                  # Kaynak (İrsaliye) satır verisine ulaş
                  # source bir SevkIrsaliyesi object'idir, kalemler child table
                  source_item = next((i for i in source.kalemler if i.name == source_item_id), None)
                  
                  if source_item:
                       remaining_qty = flt(source_item.miktar) - flt(source_item.faturalanan_miktar)
                       
                       if remaining_qty <= 0:
                            items_to_remove.append(item)
                       else:
                            item.miktar = remaining_qty
        
        # Tamamen faturalanmış satırları çıkar
        for item in items_to_remove:
             target.kalemler.remove(item)
        
        # Eğer hiç satır kalmadıysa hata ver
        if not target.kalemler:
             frappe.throw("Bu irsaliye tamamen faturalanmış!")
             
        # TUTARLARI YENİDEN HESAPLA
        # Miktarlar değiştiği için satır tutarları ve genel toplamlar bozuldu.
        target.ara_toplam = 0
        target.vergi_toplami = 0
        target.genel_toplam = 0
        target.ek_iskonto_tutari = 0
        
        for item in target.kalemler:
            # Satır Tutarı = Miktar * Birim Fiyat
            item.tutar = flt(item.miktar) * flt(item.birim_fiyat)
            
            # Ara toplama ekle
            target.ara_toplam += item.tutar
            
            # Basit Vergi Hesabı (Satırdaki oran üzerinden)
            if item.vergi_orani > 0:
                vergi_tutar = (item.tutar * item.vergi_orani) / 100
                target.vergi_toplami += vergi_tutar
                
        # Genel Toplam
        if target.vergi_dahil_mi:
             # Eğer fiyatlar vergi dahilse, ara toplam zaten genel toplam gibidir (basit mantık)
             # Ancak ERP sistemlerinde genelde birim fiyat vergi hariç tutulur.
             # Bizim yapıda 'vergi_dahil_mi' alanı var ama birim_fiyat'ın nasıl girildiği önemli.
             # Varsayım: Birim Fiyat Vergi Hariçtir.
             target.genel_toplam = target.ara_toplam + target.vergi_toplami
        else:
             target.genel_toplam = target.ara_toplam + target.vergi_toplami

        # Irsaliye referansi otomatik olarak name map ile gelir ama biz explicit olalim
        target.irsaliye_referansi = source.name

    doclist = get_mapped_doc("Sevk Irsaliyesi", source_name, {
        "Sevk Irsaliyesi": {
            "doctype": "Satis Faturasi",
            "field_map": {
                "name": "irsaliye_referansi",
                "musteri": "musteri",
                "firma": "firma",
                "sube": "sube",
                "para_birimi": "para_birimi",
                "doviz_kuru": "doviz_kuru",
                "iade_mi": "iade_mi",
                "vergi_dahil_mi": "vergi_dahil_mi",
                "odeme_kosulu": "odeme_kosulu",
                "sartlar_ve_kosullar": "sartlar_ve_kosullar",
                
                # Adresler
                "fatura_adresi": "fatura_adresi",
                "fatura_il": "fatura_il",
                "fatura_ilce": "fatura_ilce",
                "fatura_acik_adres": "fatura_acik_adres",
                
                "sevk_adresi": "sevkiyat_adresi",
                "sevkiyat_il": "sevkiyat_il",
                "sevkiyat_ilce": "sevkiyat_ilce",
                "sevkiyat_acik_adres": "sevkiyat_acik_adres",
            }
        },
        "Teslimat Kalemi": {
            "doctype": "Fatura Kalemi",
            "field_map": {
                "name": "irsaliye_kalemi_id",
                "urun": "urun",
                "urun_adi": "urun_adi", # opsiyonel
                "miktar": "miktar",
                "birim_fiyat": "birim_fiyat",
                "iskonto_orani": "iskonto_orani", # Varsa
                "vergi_sablonu": "vergi_sablonu",
                "vergi_orani": "vergi_orani",
                "depo": "depo"
            }
        }
    }, target_doc, set_missing_values)

    return doclist
