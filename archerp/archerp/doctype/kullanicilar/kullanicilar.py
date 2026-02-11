import frappe
from frappe.model.document import Document

class Kullanicilar(Document):
    def validate(self):
        if not self.e_posta:
            frappe.throw("Kullanıcı oluşturmak için E-Posta adresi zorunludur.")
            
    def before_save(self):
        self.handle_email_change()

    def handle_email_change(self):
        if self.is_new():
            return
            
        old_doc = self.get_doc_before_save()
        if not old_doc:
            return
            
        if old_doc.e_posta != self.e_posta and self.bagli_kullanici:
            # Rename the linked User document
            if frappe.db.exists("User", old_doc.e_posta):
                try:
                    frappe.rename_doc("User", old_doc.e_posta, self.e_posta, ignore_permissions=True)
                    self.bagli_kullanici = self.e_posta
                except Exception as e:
                    frappe.log_error(f"User Rename Error: {str(e)}")
                    frappe.throw(f"Kullanıcı adı güncellenirken hata oluştu: {str(e)}")

    def on_update(self):
        self.create_or_update_user()
        self.update_user_permissions()
        
    def create_or_update_user(self):
        if not self.e_posta:
            return

        # Check if user exists
        if frappe.db.exists("User", self.e_posta):
            user = frappe.get_doc("User", self.e_posta)
        else:
            user = frappe.new_doc("User")
            user.email = self.e_posta
            user.first_name = self.ad_soyad
            user.send_welcome_email = 0
            
        # Update fields
        user.first_name = self.ad_soyad
        user.enabled = 1 if self.durum == "Aktif" else 0
        
        # Password handling
        if hasattr(self, "şifre") and self.şifre:
            user.new_password = self.şifre
            
        # Bypass strict password policy to avoid "Repeats" error if settings are too high
        user.flags.ignore_password_policy = True

        # Role Sync
        # Process roles from table if it exists
        if hasattr(self, "table_wwve"):
            current_roles = []
            for row in self.table_wwve:
                role_name = row.sistem_id
                
                # Fallback if fetch field didn't populate in memory
                if not role_name and row.seçilen_rol:
                    role_name = frappe.db.get_value("Rol Tanim Formu", row.seçilen_rol, "sistem_rolu")
                
                if role_name:
                    current_roles.append(role_name)
                    
            # Overwrite roles
            user.roles = []
            for role in current_roles:
                user.append("roles", {
                    "role": role
                })
        else:
             # Fallback for legacy/manual Users without the table? 
             # If table is missing from doctype (unlikely), or not loaded.
             # If it's a new user and no table, give System Manager?
             if not user.get("roles"):
                 user.append("roles", {
                    "role": "System Manager"
                })

        user.save(ignore_permissions=True)
        
        # Link back to this document if not already linked
        if self.bagli_kullanici != user.name:
            self.db_set("bagli_kullanici", user.name)
            
    def update_user_permissions(self):
        if not self.bagli_kullanici:
            return
            
        # 1. Company Permission
        # First, remove ALL existing permissions for "Firma" to ensure clean state
        self.remove_permission("Firma")
        
        if not self.tum_firmalari_gorsun and self.firma:
            # Add specific permission only if "See All" is NOT checked
            self.set_permission("Firma", self.firma)
            
        # 2. Branch Permission
        # First, remove ALL existing permissions for "Sube"
        self.remove_permission("Sube")
        
        if not self.tum_şubeleri_gorsun and self.sube:
             # Add specific permission only if "See All" is NOT checked
            self.set_permission("Sube", self.sube)
            
        # 3. Warehouse Permission (Varsayilan Depo)
        # First, remove ALL existing permissions for "Depo"
        self.remove_permission("Depo")
        
        if self.varsayilan_depo:
            self.set_permission("Depo", self.varsayilan_depo)
            
    def set_permission(self, doctype, value):
        # We don't strictly need to check exists if we just wiped them, but it's safer
        exists = frappe.db.exists("User Permission", {
            "user": self.bagli_kullanici,
            "allow": doctype,
            "for_value": value
        })
        
        if not exists:
            perm = frappe.new_doc("User Permission")
            perm.user = self.bagli_kullanici
            perm.allow = doctype
            perm.for_value = value
            perm.is_default = 1 # Set as default
            perm.insert(ignore_permissions=True)

    def on_trash(self):
        if self.bagli_kullanici:
            user = frappe.get_doc("User", self.bagli_kullanici)
            user.enabled = 0
            user.save(ignore_permissions=True)

    def remove_permission(self, doctype):
        # Remove any existing User Permission for this doctype for this user
        frappe.db.delete("User Permission", {
            "user": self.bagli_kullanici,
            "allow": doctype
        })
        

