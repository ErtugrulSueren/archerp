
import frappe
from frappe.utils import today

def sync_subscription_to_settings(subscription_doc):
    """
    SaaS Subscription (Abonelik) bilgilerini SaaS Ayarlari (Single) dokümanına kopyalar.
    """
    settings = frappe.get_single("SaaS Ayarlari")
    
    # 1. FIELD MAPPING (JSON'dan alınan gerçek alan adları)
    # Subscription (plan_max_...) -> Settings (maksimum_...)
    
    settings.maksimum_firma = subscription_doc.plan_max_company
    settings.maksimum_sube = subscription_doc.plan_max_branch
    settings.maksimum_kullanici = subscription_doc.plan_max_user
    
    # Tarih alanı (end_date -> paket_bitis_tarihi)
    settings.paket_bitis_tarihi = subscription_doc.end_date
    
    # Pro Paket (is_pro -> pro_paket_mi)
    settings.pro_paket_mi = subscription_doc.is_pro

    # Ayarları kaydet
    settings.save(ignore_permissions=True)
    frappe.msgprint("SaaS Ayarları güncellendi.")


def check_limits(doc, method=None):
    """
    SaaS limitlerini kontrol eder.
    Firma, Sube veya User oluşturulmadan önce (before_insert) çalışmalıdır.
    """
    
    # 1. SaaS Ayarlarını (Single DocType) getir
    settings = frappe.get_single("SaaS Ayarlari")
    
    # -----------------------------------------------
    # 0. SÜRE KONTROLÜ
    # -----------------------------------------------
    if settings.paket_bitis_tarihi and settings.paket_bitis_tarihi < today():
        frappe.throw(
            title="Abonelik Süresi Doldu",
            msg="Abonelik süreniz dolmuştur. İşlem yapmak için lütfen süreyi uzatınız.<br>Sistem Yöneticisi ile iletişime geçin.",
            exc=frappe.PermissionError
        )

    # -----------------------------------------------
    # FIRMA LİMİT KONTROLÜ
    # -----------------------------------------------
    if doc.doctype == "Firma":
        current_count = frappe.db.count("Firma")
        max_limit = settings.maksimum_firma
        
        if current_count >= max_limit:
            frappe.throw(
                title="Paket Limiti Aşıldı",
                msg=f"Maksimum Firma sayısına ({max_limit}) ulaştınız. Yeni firma ekleyemezsiniz.<br>Lütfen paketinizi yükseltin.",
                exc=frappe.PermissionError
            )

    # -----------------------------------------------
    # ŞUBE LİMİT KONTROLÜ
    # -----------------------------------------------
    elif doc.doctype == "Sube":
        current_count = frappe.db.count("Sube")
        max_limit = settings.maksimum_sube
        
        if current_count >= max_limit:
            frappe.throw(
                title="Paket Limiti Aşıldı",
                msg=f"Maksimum Şube sayısına ({max_limit}) ulaştınız. Yeni şube ekleyemezsiniz.<br>Lütfen paketinizi yükseltin.",
                exc=frappe.PermissionError
            )

    # -----------------------------------------------
    # KULLANICI LİMİT KONTROLÜ
    # -----------------------------------------------
    elif doc.doctype == "User":
        if doc.user_type != "System User":
            return

        current_count = frappe.db.count("User", filters={
            "user_type": "System User", 
            "enabled": 1,
            "name": ["not in", ["Administrator", "Guest"]]
        })
        
        max_limit = settings.maksimum_kullanici
        
        if current_count >= max_limit:
            frappe.throw(
                title="Paket Limiti Aşıldı",
                msg=f"Maksimum Kullanıcı sayısına ({max_limit}) ulaştınız. Yeni kullanıcı ekleyemezsiniz.<br>Lütfen paketinizi yükseltin.",
                exc=frappe.PermissionError
            )
