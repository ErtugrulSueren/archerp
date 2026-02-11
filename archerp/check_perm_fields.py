import frappe

def check():
    try:
        role_name = "_TestRole_" + frappe.generate_hash()
        if not frappe.db.exists("Role", role_name):
            r = frappe.new_doc("Role")
            r.role_name = role_name
            r.save()

        # Try to add 'submit' permission to 'User' DocType which is not submittable
        p = frappe.new_doc("Custom DocPerm")
        p.parent = "User"
        p.role = role_name
        p.read = 1
        p.submit = 1  # User is not submittable
        p.cancel = 1
        p.amend = 1
        p.insert(ignore_permissions=True)
        
        print("SUCCESS: Permission inserted even if not supported.")
        
        # Cleanup
        p.delete()
        frappe.delete_doc("Role", role_name)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")

check()
