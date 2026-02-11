import frappe
from frappe.model.document import Document

class RolTanimFormu(Document):
    def on_update(self):
        # Create Role if it doesn't exist
        if not frappe.db.exists("Role", self.rol_adi):
            role = frappe.new_doc("Role")
            role.role_name = self.rol_adi
            role.desk_access = 1 # Assuming desk access is needed
            role.insert(ignore_permissions=True)
            
        # Link the system role field
        if self.sistem_rolu != self.rol_adi:
            self.db_set("sistem_rolu", self.rol_adi)
            
        self.update_system_permissions()

    def update_system_permissions(self):
        role_name = self.rol_adi
        
        # Keep track of updated doctypes to handle deletions
        updated_doctypes = []
        
        if hasattr(self, "yetkiler"):
            for row in self.yetkiler:
                if not row.ilgili_doctype:
                    continue
                    
                updated_doctypes.append(row.ilgili_doctype)
                
                # Check if Custom DocPerm exists
                name = frappe.db.exists("Custom DocPerm", {
                    "role": role_name,
                    "parent": row.ilgili_doctype
                })
                
                if name:
                    docperm = frappe.get_doc("Custom DocPerm", name)
                else:
                    docperm = frappe.new_doc("Custom DocPerm")
                    docperm.parent = row.ilgili_doctype
                    docperm.role = role_name
                    
                # Map fields
                docperm.read = row.okuma
                docperm.write = row.yazma
                docperm.create = row.olustur
                docperm.delete = row.sil
                docperm.submit = row.gonder
                docperm.cancel = row.iptal
                docperm.amend = row.degistirme
                docperm.report = row.rapor
                docperm.export = row.disa_aktar
                docperm.select = row.secim
                
                docperm.save(ignore_permissions=True)
        
        # Delete permissions that are removed from the table
        # We find all Custom DocPerms for this role
        existing_perms = frappe.get_all("Custom DocPerm", filters={"role": role_name}, fields=["name", "parent"])
        for perm in existing_perms:
            if perm.parent not in updated_doctypes:
                frappe.delete_doc("Custom DocPerm", perm.name, ignore_permissions=True)
            
    def after_rename(self, old_dn, new_dn, merge=False):
        # Rename the corresponding Role
        if frappe.db.exists("Role", old_dn):
            frappe.rename_doc("Role", old_dn, new_dn, ignore_permissions=True)
            
    def on_trash(self):
        # Delete the corresponding Role
        if frappe.db.exists("Role", self.rol_adi):
            frappe.delete_doc("Role", self.rol_adi, ignore_permissions=True)
