# Copyright (c) 2025, Ertu and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Firma(Document):
    def after_insert(self):
        """
        Firma ilk kez oluşturulduğunda standart hesap planını oluşturur.
        """
        self.create_standard_coa()

    def create_standard_coa(self):
        # Kök Hesaplar (Root Accounts)
        root_accounts = [
            {"account_name": "Varlıklar", "type": "Asset", "root_type": "Asset", "is_group": 1},
            {"account_name": "Yükümlülükler", "type": "Liability", "root_type": "Liability", "is_group": 1},
            {"account_name": "Özkaynaklar", "type": "Equity", "root_type": "Equity", "is_group": 1},
            {"account_name": "Gelirler", "type": "Income", "root_type": "Income", "is_group": 1},
            {"account_name": "Giderler", "type": "Expense", "root_type": "Expense", "is_group": 1},
        ]

        # Alt Hesaplar (Basic Child Accounts)
        # Format: (Parent Name, Account Name, Account Type, Is Group)
        child_accounts = [
            ("Varlıklar", "Dönen Varlıklar", "Asset", 1),
            ("Dönen Varlıklar", "Kasa", "Cash", 1),
            ("Dönen Varlıklar", "Banka", "Bank", 1),
            ("Yükümlülükler", "Kısa Vadeli Yükümlülükler", "Liability", 1),
            ("Gelirler", "Satış Gelirleri", "Income", 1),
            ("Giderler", "Yönetim Giderleri", "Expense", 1),
        ]

        # 1. Kök Hesapları Oluştur
        for acc in root_accounts:
            if not frappe.db.exists("Hesap", {"account_name": acc["account_name"], "firma": self.name}):
                new_acc = frappe.new_doc("Hesap")
                new_acc.update({
                    "account_name": acc["account_name"],
                    "firma": self.name,
                    "parent_account": None, # Root hesabın parent'ı yoktur
                    "is_group": acc["is_group"],
                    "account_type": acc.get("account_type", ""),
                    "root_type": acc["root_type"],
                    "report_type": "Balance Sheet" if acc["root_type"] in ["Asset", "Liability", "Equity"] else "Profit and Loss"
                })
                new_acc.insert(ignore_permissions=True)

        # 2. Alt Hesapları Oluştur
        for parent_name, acc_name, acc_type, is_group in child_accounts:
            # Parent hesabın tam adını bul (Firma ile eşleşen)
            parent_acc = frappe.db.get_value("Hesap", {"account_name": parent_name, "firma": self.name}, "name")
            
            if parent_acc and not frappe.db.exists("Hesap", {"account_name": acc_name, "firma": self.name}):
                new_child = frappe.new_doc("Hesap")
                new_child.update({
                    "account_name": acc_name,
                    "firma": self.name,
                    "parent_account": parent_acc,
                    "is_group": is_group,
                    "root_type": frappe.db.get_value("Hesap", parent_acc, "root_type"), # Parent'tan miras al
                    "report_type": frappe.db.get_value("Hesap", parent_acc, "report_type")
                })
                # Özel Account Type varsa ayarla
                if acc_type in ["Cash", "Bank"]:
                     new_child.account_type = acc_type
                
                new_child.insert(ignore_permissions=True)
