
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class StokCikisFisi(Document):
    def validate(self):
        """
        Kayıt öncesi stok kontrolü.
        """
        for item in self.kalemler:
            # Depodaki güncel stoğu sorgula
            current_qty = frappe.db.get_value("Stok Bakiyesi", 
                {"urun": item.urun, "depo": self.kaynak_depo}, 
                "mevcut_miktar"
            ) or 0.0
            
            issue_qty = flt(item.cikis_miktari)
            
            if issue_qty > current_qty:
                frappe.throw(
                    msg=f"Yetersiz Stok! Satır {item.idx}: '{item.urun}' ürünü için '{self.kaynak_depo}' deposunda yeterli miktar yok. (Mevcut: {current_qty}, İstenen: {issue_qty})",
                    title="Stok Hatası"
                )

    def on_submit(self):
        """
        Fiş onaylandığında stoktan düş.
        """
        self.make_stock_entry(reverse=False)
        self.make_gl_entries(cancel=False)

    def on_cancel(self):
        """
        Fiş iptal edildiğinde stoğu geri al.
        """
        self.make_stock_entry(reverse=True)
        self.make_gl_entries(cancel=True)

    def make_stock_entry(self, reverse=False):
        """
        Stok Defteri kaydı oluşturur.
        uses shared stock_ledger.py
        """
        from archerp.controllers.stock_ledger import create_stock_entry
        
        # Normal (submit): Stoktan Çıkış (-1)
        # İptal (cancel): Stoğa Giriş (Geri alma) (+1)
        
        # Çıkış işlemi olduğu için base multiplier -1'dir.
        # Reverse (İptal) durumunda bu -1 ile çarpılır -> +1 olur.
        base_multiplier = -1 
        action_multiplier = -1 if reverse else 1
        
        final_multiplier = base_multiplier * action_multiplier

        for item in self.kalemler:
            qty = flt(item.cikis_miktari)
            signed_qty = qty * final_multiplier
            
            # Warehouse logic: 'depo' field isn't on item line in Stok Cikis, it's 'kaynak_depo' on Header
            create_stock_entry(self, item, signed_qty, reverse=reverse, warehouse_field="kaynak_depo")

    def make_gl_entries(self, cancel=False):
        """
        Muhasebe Kayıtları Oluştur (GL Entry).
        Stok (Varlık) -> Gider (Masraf)
        Uses shared generic_ledger.py
        """
        from archerp.controllers.general_ledger import create_gl_entry
        
        # Gider Hesabı (Borç)
        expense_account = self.gider_hesabi
        if not expense_account:
            frappe.throw("Muhasebe kaydı için 'Gider Hesabı' zorunludur.")

        # Tarih
        # posting_date = self.tarih or frappe.utils.today()
        # The generic util takes 'doc' which has 'tarih', so we don't need to pass date explicitly unless we override.
        # But 'create_gl_entry' signature is (doc, account, debit, credit, cancel, party_type, party, remark).
        
        # Her kalem için GL oluştur
        for item in self.kalemler:
            amount = flt(item.cikis_miktari) * flt(item.birim_maliyet)
            
            if amount == 0:
                continue

            # 1. Stok Hesabını Bul (Depo'dan)
            warehouse_stock_account = frappe.db.get_value("Depo", self.kaynak_depo, "stok_hesabi")
            
            # Firma bilgisi dökümanın kendisinde (self.firma)
            company = getattr(self, "firma", None)
            if not company:
                company = frappe.defaults.get_user_default("Company")
            
            stock_account = warehouse_stock_account
            
            # Eğer depoda özel hesap yoksa firmanın varsayılanını al
            if not stock_account and company:
                 stock_account = frappe.db.get_value("Firma", company, "varsayilan_stok_hesabi")

            if not stock_account:
                frappe.throw(f"'{self.kaynak_depo}' deposu için Stok Hesabı tanımlanamadı. Lütfen Depo veya Firma ayarlarını kontrol edin.")

            # YÖN BELİRLEME
            # Normal:
            #   Borç (Debit): Gider Hesabı
            #   Alacak (Credit): Stok Hesabı
            
            debit_account = expense_account
            credit_account = stock_account
            
            # Kayıt Oluştur
            
            # 1. DEBIT (Gider)
            create_gl_entry(
                doc=self,
                account=debit_account,
                debit=amount,
                credit=0,
                cancel=cancel,
                remark=f"Stok Çıkışı: {self.name} - {self.cikis_tipi}"
            )
            
            # 2. CREDIT (Stok)
            create_gl_entry(
                doc=self,
                account=credit_account,
                debit=0,
                credit=amount,
                cancel=cancel,
                remark=f"Stok Çıkışı: {self.name} - {self.cikis_tipi}"
            )
