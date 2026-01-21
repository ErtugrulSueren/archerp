import frappe
from frappe.model.document import Document

class Tedarikci(Document):
    def after_insert(self):
        # 320.001 Ana Hesabını Bul (Yurtiçi Satıcılar)
        parent_account = frappe.db.get_value("Hesap", 
            {"hesap_kodu": "320.001", "is_group": 1}, 
            "name"
        )
        
        if not parent_account:
            frappe.msgprint("Uyarı: '320.001' kodlu Ana Hesap Grubu (Yurtiçi Satıcılar) bulunamadı. Lütfen önce bu grubu oluşturun.")
            return

        # Parent Hesap Kodunu al
        parent_doc = frappe.get_doc("Hesap", parent_account)
        parent_code = parent_doc.hesap_kodu
        
        # Yeni Hesap Kodu Hesapla (Örn: 320.001.001)
        new_code = ""
        if parent_code:
            # Bu parent'a bağlı en son(büyük) hesap kodunu bul
            # Sort by LENGTH first to ensure 1000 > 999
            last_account = frappe.db.sql("""
                SELECT hesap_kodu FROM `tabHesap` 
                WHERE parent_hesap = %s AND hesap_kodu LIKE %s 
                ORDER BY LENGTH(hesap_kodu) DESC, hesap_kodu DESC LIMIT 1
            """, (parent_account, parent_code + ".%"))
            
            if last_account and last_account[0][0]:
                last_code = last_account[0][0]
                # Kodun sonundaki sayıyı bulmaya çalış (noktadan sonraki)
                parts = last_code.split('.')
                if len(parts) > 2 and parts[-1].isdigit(): # 320.001.001
                    next_seq = int(parts[-1]) + 1
                    new_code = f"{parent_code}.{str(next_seq).zfill(3)}"
                else:
                    # Format farklıysa düz mantık ekle
                    new_code = f"{parent_code}.001"
            else:
                # Hiç alt hesap yoksa ilkini oluştur
                new_code = f"{parent_code}.001"

        # Yeni Hesap Oluştur
        try:
            new_account = frappe.new_doc("Hesap")
            new_account.hesap_adi = self.tedarikci_adi
            new_account.hesap_kodu = new_code # Kod ataması
            new_account.parent_hesap = parent_account
            new_account.account_type = "Borç (Payable)"
            new_account.is_group = 0
            new_account.para_birimi = "TRY"
            new_account.insert(ignore_permissions=True)
            
            # Tedarikçi Kartına Bağla
            self.db_set("muhasebe_hesabi", new_account.name)
            
            frappe.msgprint(f"Bilgi: '{new_account.hesap_adi}' ({new_account.hesap_kodu}) muhasebe hesabı otomatik oluşturuldu.")
            
        except Exception as e:
            frappe.msgprint(f"Hata: Muhasebe hesabı oluşturulurken bir sorun oluştu: {str(e)}")
