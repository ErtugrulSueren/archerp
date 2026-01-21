# Copyright (c) 2025, Ertu and contributors
# For license information, please see license.txt

# import frappe
from frappe.utils.nestedset import NestedSet


class MusteriGrubu(NestedSet):
    def on_update(self):
        super(MusteriGrubu, self).on_update()
