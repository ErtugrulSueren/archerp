import frappe
from frappe.model.document import Document
from frappe.utils import flt, today
from frappe.model.mapper import get_mapped_doc

class MalKabulFisi(Document):
    def validate(self):
        """
        Kaydetme öncesi sunucu taraflı hesaplama ve doğrulama.
        """
        if self.docstatus == 0:
            self.calculate_totals()

    def calculate_totals(self):
        """
        JS'teki hesaplama mantığının Python kopyası. Güvenlik için.
        """
        total_net = 0.0
        total_tax = 0.0
        
        # Helper bool
        tax_inclusive = self.vergi_dahil_mi == 1 or self.vergi_dahil_mi == "1"

        for item in self.kalemler:
            qty = flt(item.miktar)
            price = flt(item.birim_fiyat)
            tax_rate = flt(item.vergi_orani)
            
            # --- Hesaplama Motoru ---
            if tax_inclusive:
                # İçinden vergiyi ayıkla
                # Net = Fiyat / (1 + Rate/100)
                net_unit_price = price / (1 + (tax_rate / 100.0))
                unit_tax = price - net_unit_price
            else:
                # Üstüne vergi ekle
                net_unit_price = price
                unit_tax = net_unit_price * (tax_rate / 100.0)
            
            if item.tur == "Hizmet":
                # Hizmet ise Gelir Gider Kalemi'nden hesabı çek
                if item.gelir_gider_kalemi and not item.muhasebe_hesabi:
                    acc = frappe.db.get_value("Gelir Gider Kalemi", item.gelir_gider_kalemi, "varsayilan_hesap")
                    item.muhasebe_hesabi = acc
            else:
                # Stok ise Ürün'den Gider Hesabını çek (Bilgi amaçlı, burada GL atılmaz ama faturada lazım olabilir)
                if item.urun and not item.muhasebe_hesabi:
                    acc = frappe.db.get_value("Urun", item.urun, "gider_hesabi")
                    item.muhasebe_hesabi = acc

            line_net = qty * net_unit_price
            line_tax = qty * unit_tax
            
            # Child alanı güncelle (Veri tutarlılığı için)
            item.tutar = line_net 
            item.birim_maliyet = net_unit_price  # Maliyeti sakla
            
            # Akümülatörler
            total_net += line_net
            total_tax += line_tax
             
        # Parent güncelle
        self.ara_toplam = total_net
        self.vergi_toplami = total_tax
        
        # Genel Toplam = Net + Vergi - İskonto
        discount = flt(self.ek_iskonto_tutari)
        grand_total = total_net + total_tax - discount
        
        if grand_total < 0:
            grand_total = 0.0
            
        self.genel_toplam = grand_total
 
    def on_submit(self):
        """
        Stok Hareketi Oluştur (Normal veya İade).
        """
        self.make_stock_entry(reverse=False)
        self.make_gl_entries(cancel=False)
        self.guncelle_durum()
        self.siparis_guncelle()
 
    def on_cancel(self):
        """
        Stok Hareketini Geri Al (Ters Kayıt).
        """
        # Check if any invoices are linked to this receipt
        linked_invoices = frappe.db.sql("""
            SELECT DISTINCT saf.name, saf.docstatus
            FROM `tabSatin Alma Faturasi` saf
            WHERE saf.ilgili_mal_kabul = %s
            AND saf.docstatus != 2
        """, (self.name,), as_dict=True)
        
        if linked_invoices:
            # Check if any are submitted (docstatus = 1)
            submitted_invoices = [inv.name for inv in linked_invoices if inv.docstatus == 1]
            if submitted_invoices:
                invoice_list = ", ".join(submitted_invoices)
                frappe.throw(
                    f"Bu Mal Kabul Fişi için fatura(lar) kesilmiş: {invoice_list}. "
                    f"Önce faturaları iptal etmelisiniz.",
                    title="İptal Edilemiyor"
                )
        
        # If no linked invoices or all are cancelled, proceed with cancellation
        self.make_stock_entry(reverse=True)
        self.make_gl_entries(cancel=True)
        self.siparis_guncelle()
        
        # Update status after cancel - use db_set since document is already in save transaction
        frappe.db.set_value(self.doctype, self.name, 'status', 'İptal', update_modified=False)
        
    def make_gl_entries(self, cancel=False):
        """
        Sürekli Envanter (Perpetual Inventory) Muhasebe Kayıtları
        """
        # Şirket Ayarlarını Çek
        company_settings = frappe.db.get_value("Firma", self.firma, 
            ["mal_kabul_hesabi", "varsayilan_stok_hesabi"], as_dict=True)
        
        # Check if company settings exist
        if not company_settings:
            # Company settings not found, skip GL entries
            return
            
        credit_account = company_settings.get("mal_kabul_hesabi")
        default_stock_account = company_settings.get("varsayilan_stok_hesabi")
        
        if not credit_account:
             # Eğer ayar yoksa muhasebe kaydı atma (veya hata ver, ama esnek olalım)
             # Kullanıcı GL istemiyorsa boş bırakmıştır.
             return
 
        # YÖN BELİRLEME
        # Normal (Alış): Stok (Borç) / Mal Kabul (Alacak)
        # İade (Çıkış): Mal Kabul (Borç) / Stok (Alacak)
        
        is_return = self.iade_mi == 1 or self.iade_mi == "1"
        
        # GL Listesi
        gl_entries = []
        
        for item in self.kalemler:
             # Hizmet Kalemleri Stok Hareketi Yaratmaz -> GL Atma
             if item.tur == "Hizmet":
                  continue
             
             amount = flt(item.tutar) # Net Tutar (Vergi Hariç)
             if amount == 0: continue
             
             # 1. Stok Hesabını Bul (Depo > Firma)
             warehouse_account = frappe.db.get_value("Depo", item.depo, "stok_hesabi")
             stock_account = warehouse_account or default_stock_account
             
             if not stock_account:
                  frappe.throw(f"'{item.depo}' deposu için Stok Hesabı tanımlı değil ve Firma varsayılanı yok!")
             
             # Alış:
             # Borç: Stok Hesabı
             # Alacak: Mal Kabul Hesabı (Contra)
             
             # İade:
             # Borç: Mal Kabul Hesabı
             # Alacak: Stok Hesabı
             
             # İptal (Cancel): Tam tersi
             
             # Temel Yön (Normal İşlem İçin)
             if not is_return:
                  debit_account = stock_account
                  credit_acct = credit_account # variable name conflict prevention
             else:
                  debit_account = credit_account
                  credit_acct = stock_account
                  
             # Kayıt At
             # DEBIT
             self.create_gl_entry(debit_account, amount, 0, cancel, "Tedarikci", self.tedarikci)
             
             # CREDIT
             self.create_gl_entry(credit_acct, 0, amount, cancel, "Tedarikci", self.tedarikci)
             
    def create_gl_entry(self, account, debit, credit, cancel, party_type=None, party=None):
        if debit == 0 and credit == 0: return

        gl = frappe.new_doc("Muhasebe Defteri")
        gl.belge_tipi = "Mal Kabul Fisi"
        gl.belge_no = self.name
        gl.tarih = self.tarih
        gl.hesap = account
        gl.aciklama = f"Mal Kabul: {self.name} - {self.tedarikci}"
        gl.muhatap_tipi = party_type
        gl.carimuhatap = party
        
        if cancel:
             gl.borc = credit
             gl.alacak = debit
        else:
             gl.borc = debit
             gl.alacak = credit
             
        gl.insert(ignore_permissions=True)
        if self.satin_alma_siparisi_referansi:
             siparis = frappe.get_doc("Satin Alma Siparisi", self.satin_alma_siparisi_referansi)
             siparis.guncelle_teslim_alinan()

    def fatura_guncelle(self):
        """
        Satin Alma Faturasi submit/cancel olduğunda çağrılır.
        """
        # Sıfırla
        for item in self.kalemler:
            item.faturalanan_miktar = 0.0
            
        fatura_kalemleri = frappe.db.sql("""
            SELECT safk.mal_kabul_kalemi_id, SUM(safk.miktar) as fatura_miktar
            FROM `tabSatin Alma Fatura Kalemi` safk
            JOIN `tabSatin Alma Faturasi` saf ON safk.parent = saf.name
            WHERE saf.docstatus = 1 AND safk.mal_kabul_kalemi_id IN (
                SELECT name FROM `tabMal Kabul Kalemi` WHERE parent = %s
            )
            GROUP BY safk.mal_kabul_kalemi_id
        """, (self.name), as_dict=True)
        
        for row in fatura_kalemleri:
            for item in self.kalemler:
                if item.name == row.mal_kabul_kalemi_id:
                    item.faturalanan_miktar = flt(row.fatura_miktar)
        
        self.save(ignore_permissions=True)
        self.guncelle_durum()

    def guncelle_durum(self):
        """
        Frappe standard: Update custom status field based on docstatus and other factors
        Note: Use direct assignment (self.status) during save/cancel, db_set() for outside updates
        """
        # Cancelled documents
        if self.docstatus == 2:
            self.status = 'İptal'
            return
        
        # Draft documents
        if self.docstatus == 0:
            self.status = 'Taslak'
            return
        
        # Submitted documents (docstatus == 1)
        if self.docstatus != 1:
            return

        toplam_miktar = 0
        toplam_fatura = 0

        for item in self.kalemler:
            toplam_miktar += flt(item.miktar)
            toplam_fatura += flt(item.faturalanan_miktar)

        status = "Faturalanacak" # Varsayılan (Submit sonrası)
        
        if self.iade_mi:
             status = "İade"
        elif toplam_fatura >= toplam_miktar:
            status = "Tamamlandı"
        elif toplam_fatura > 0:
            status = "Kısmi Faturalandı"
        else:
            status = "Faturalanacak"
             
        self.status = status

    def make_stock_entry(self, reverse=False):
        """
        Stok Defteri kaydı oluşturur.
        Uses shared stock_ledger.py
        """
        from archerp.controllers.stock_ledger import create_stock_entry
        
        is_return = self.iade_mi
        
        # Miktar Çarpanı
        # Alış = Giriş (+), İade = Çıkış (-)
        direction = -1 if is_return else 1
        
        for item in self.kalemler:
            if item.tur == "Hizmet": continue

            raw_qty = flt(item.miktar)
            signed_qty = raw_qty * direction
            
            # Warehouse logic: Item depo or header hedef_depo
            # We can pass 'depo' as field, but logic in util will handle fallback if item has no valid warehouse field
            # But wait, Mal Kabul Items might have 'depo', but header has 'hedef_depo'
            # Let's ensure item has the correct warehouse set before calling, or rely on util fallback
            
            # Use 'depo' field if it exists on item, otherwise util will look for 'hedef_depo' on doc if passed field is empty?
            # Util logic: wahouse = item.get(field); if not w: w = doc.get(field); if not w: w = doc.hedef_depo
            # So passing "depo" is safe.
            
            create_stock_entry(self, item, signed_qty, reverse=reverse, warehouse_field="depo")
    
    def siparis_guncelle(self):
        """
        Satın Alma Siparişi durumunu güncelle.
        TODO: Implement order status update logic when purchase order integration is added
        """
        # Placeholder - prevents AttributeError
        pass

@frappe.whitelist()
def make_purchase_invoice(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.tarih = today()
        target.vade_tarihi = today()
        target.ilgili_mal_kabul = source.name
        
        # 1. Alacak Hesabı (Tedarikçiden)
        if target.tedarikci:
             target.alacak_hesabi = frappe.db.get_value("Tedarikci", target.tedarikci, "muhasebe_hesabi")

        # 2. Gider Hesapları (Ürünlerden)
        for item in target.kalemler:
             if item.urun and not item.gider_hesabi:
                  item.gider_hesabi = frappe.db.get_value("Urun", item.urun, "gider_hesabi")
        items_to_remove = []
        for item in target.kalemler:
             source_item_id = item.mal_kabul_kalemi_id
             if source_item_id:
                  source_item = next((i for i in source.kalemler if i.name == source_item_id), None)
                  if source_item:
                       remaining = flt(source_item.miktar) - flt(source_item.faturalanan_miktar)
                       if remaining <= 0:
                            items_to_remove.append(item)
                       else:
                            item.miktar = remaining
        
        for item in items_to_remove:
             target.kalemler.remove(item)
             
        if not target.kalemler:
             frappe.throw("Bu irsaliyenin tüm kalemleri zaten faturalanmış!")

    doclist = get_mapped_doc("Mal Kabul Fisi", source_name, {
        "Mal Kabul Fisi": {
            "doctype": "Satin Alma Faturasi",
            "field_map": {
                "name": "ilgili_mal_kabul",
                "tedarikci": "tedarikci",
                "sube": "sube",
                "para_birimi": "para_birimi",
                "doviz_kuru": "doviz_kuru",
                "hedef_depo": "hedef_depo",
                "odeme_kosulu": "odeme_kosulu",
                "sartlar_ve_kosullar": "sartlar_ve_kosullar",
                "vergi_dahil_mi": "vergi_dahil_mi",
                "satin_alma_siparisi_referansi": "satin_alma_siparisi_referansi"
            }
        },
        "Mal Kabul Kalemi": {
            "doctype": "Satin Alma Fatura Kalemi",
            "field_map": {
                "name": "mal_kabul_kalemi_id",
                "siparis_kalemi_id": "siparis_kalemi_id",
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
