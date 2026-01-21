
import frappe
from frappe.model.document import Document
from archerp.saas.utils import sync_subscription_to_settings

class SaaSSubscription(Document):
    def validate(self):
        """
        Tekil Aktiflik Kontrolü:
        Eğer bu kayıt Aktif ("Active") yapılıyorsa, diğer tüm aktif abonelikleri 
        "Suspended" durumuna çeker.
        """
        # Status kontrolü: JSON'da options "Active, Expired, Suspended" olarak tanımlı.
        if self.durum == "Active":
            # Kendisi dışındaki diğer aktif kayıtları bul
            others = frappe.get_all("SaaS Subscription", 
                                   filters={
                                       "durum": "Active",
                                       "name": ["!=", self.name]
                                   })
            
            # Bulunan diğer kayıtları Pasif (Suspended) yap
            if others:
                for other in others:
                    frappe.db.set_value("SaaS Subscription", other.name, "durum", "Suspended")
                
                frappe.msgprint(f"{len(others)} adet eski aktif abonelik otomatik olarak Askıya Alındı (Suspended).")

    def on_update(self):
        if self.durum == "Active":
             sync_subscription_to_settings(self)

    def on_submit(self):
        if self.durum == "Active":
            sync_subscription_to_settings(self)

    def on_trash(self):
        """
        Aktif aboneliklerin silinmesini engeller.
        """
        if self.durum == "Active":
            frappe.throw(
                title="Abonelik Silinemez",
                msg="Aktif durumdaki bir aboneliği silemezsiniz.<br>Önce durumu 'Suspended' veya 'Expired' yapınız.",
                exc=frappe.PermissionError
            )
