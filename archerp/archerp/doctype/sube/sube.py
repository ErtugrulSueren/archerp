# Copyright (c) 2025, Ertu and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Sube(Document):
    def after_insert(self):
        """Sube olusturuldugunda otomatik Kasa hesabi olustur."""
        self.create_kasa_account()

    def create_kasa_account(self):
        """
        Sube icin 'Kasa' hesabi olusturur.
        Parent olarak Nakit (Cash) tipinde grup hesabi kullanir.
        Hesap adi: '{sube_adi} Kasa TL'
        """
        # Kasa grup hesabini bul (account_type = Nakit (Cash), is_group = 1)
        kasa_parent = frappe.db.get_value(
            "Hesap",
            {"account_type": "Nakit (Cash)", "is_group": 1},
            "name"
        )

        if not kasa_parent:
            # Fallback: hesap_adi icinde 'Kasa' gecen grup hesabi ara
            kasa_parent = frappe.db.get_value(
                "Hesap",
                {"hesap_adi": ["like", "%Kasa%"], "is_group": 1},
                "name"
            )

        if not kasa_parent:
            frappe.msgprint(
                f"Kasa grup hesabi bulunamadi. '{self.sube_adi}' subesi icin kasa hesabi otomatik olusturulamadi.",
                title="Uyari",
                indicator="orange"
            )
            return

        hesap_adi = f"{self.sube_adi} Kasa TL"

        # Ayni isimde hesap varsa tekrar olusturma
        if frappe.db.exists("Hesap", {"hesap_adi": hesap_adi}):
            frappe.msgprint(
                f"'{hesap_adi}' hesabi zaten mevcut.",
                title="Bilgi",
                indicator="blue"
            )
            return

        hesap = frappe.new_doc("Hesap")
        hesap.hesap_adi = hesap_adi
        hesap.parent_hesap = kasa_parent
        hesap.account_type = "Nakit (Cash)"
        hesap.is_group = 0
        hesap.para_birimi = "TRY"
        hesap.firma = self.bagli_firma
        hesap.sube = self.name
        hesap.insert(ignore_permissions=True)

        frappe.msgprint(
            f"'{hesap_adi}' kasa hesabi basariyla olusturuldu.",
            title="Hesap Olusturuldu",
            indicator="green"
        )
