import frappe
from frappe.utils.nestedset import NestedSet

class Depo(NestedSet):
    def on_update(self):
        super(Depo, self).on_update()
