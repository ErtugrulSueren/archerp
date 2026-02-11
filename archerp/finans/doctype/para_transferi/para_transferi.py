import frappe
from frappe.model.document import Document
from frappe.utils import flt

class ParaTransferi(Document):
    def validate(self):
        if self.docstatus == 0:
            self.status = "Taslak"
            
        if self.gonderen_hesap == self.alici_hesap:
            frappe.throw("Gönderen ve Alıcı hesap aynı olamaz.")
            
        if flt(self.tutar) <= 0:
            frappe.throw("Tutar 0'dan büyük olmalı.")
            
    def on_submit(self):
        self.db_set("status", "Tamamlandı")
        self.make_gl_entries(cancel=False)
        
    def on_cancel(self):
        self.db_set("status", "İptal")
        self.make_gl_entries(cancel=True)
        
    def make_gl_entries(self, cancel=False):
        gl_entries = []
        
        # 1. Ana Transfer (Sender -> Receiver)
        amount = flt(self.tutar)
        exchange_rate = flt(self.doviz_kuru) or 1.0
        
        base_amount = amount * exchange_rate
        
        # Gonderen (Alacak / Credit)
        self.create_gl_entry(
            account=self.gonderen_hesap,
            debit=0,
            credit=base_amount,
            cancel=cancel,
            description=f"Transfer Gönderimi: {self.name} -> {self.alici_hesap}"
        )
        
        # Alici (Borc / Debit)
        self.create_gl_entry(
            account=self.alici_hesap,
            debit=base_amount,
            credit=0,
            cancel=cancel,
            description=f"Transfer Alımı: {self.name} <- {self.gonderen_hesap}"
        )
        
        # 2. Masraf (Varsa)
        expense_amount = flt(self.masraf_tutari)
        if expense_amount > 0:
            if not self.masraf_hesabi:
                frappe.throw("Masraf tutarı girilmiş ancak Masraf Hesabı seçilmemiş.")
                
            base_expense = expense_amount * exchange_rate
            
            # Gonderen (Alacak / Credit) - Masrafı da gönderen öder
            self.create_gl_entry(
                account=self.gonderen_hesap,
                debit=0,
                credit=base_expense,
                cancel=cancel,
                description=f"Transfer Masrafı: {self.name}"
            )
            
            # Masraf Hesabı (Borc / Debit)
            self.create_gl_entry(
                account=self.masraf_hesabi,
                debit=base_expense,
                credit=0,
                cancel=cancel,
                description=f"Transfer Masrafı: {self.name}"
            )

    def create_gl_entry(self, account, debit, credit, cancel, description):
        gl = frappe.new_doc("Muhasebe Defteri")
        gl.belge_tipi = "Para Transferi"
        gl.belge_no = self.name
        gl.tarih = self.tarih
        gl.hesap = account
        gl.aciklama = description or self.aciklama
        
        # Firma ve Şube (Varsa)
        if self.firma:
            gl.firma = self.firma
        if hasattr(self, "sube") and self.sube:
            gl.sube = self.sube
        
        if cancel:
            gl.borc = credit
            gl.alacak = debit
        else:
            gl.borc = debit
            gl.alacak = credit
            
        gl.insert(ignore_permissions=True)
