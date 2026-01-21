// Copyright (c) 2025, Ertu and contributors
// For license information, please see license.txt

frappe.ui.form.on("Para Transferi", {
    onload: function (frm) {
        if (!frm.doc.firma) {
            frappe.db.get_list('Firma', {
                fields: ['name'],
                limit: 2
            }).then(records => {
                if (records.length === 1) {
                    frm.set_value('firma', records[0].name);
                }
            });
        }
    },
    firma: function (frm) {
        if (frm.doc.firma) {
            frappe.db.get_value('Firma', frm.doc.firma, 'varsayilan_banka_masraf_hesabi')
                .then(r => {
                    if (r && r.message && r.message.varsayilan_banka_masraf_hesabi) {
                        frm.set_value('masraf_hesabi', r.message.varsayilan_banka_masraf_hesabi);
                    }
                });
        }
    },
    setup: function (frm) {
        frm.set_query("gonderen_hesap", function () {
            return {
                filters: {
                    "is_group": 0,
                    "account_type": ["in", ["Banka (Bank)", "Nakit (Cash)"]]
                }
            };
        });

        frm.set_query("alici_hesap", function () {
            return {
                filters: {
                    "is_group": 0,
                    "account_type": ["in", ["Banka (Bank)", "Nakit (Cash)"]]
                }
            };
        });

        frm.set_query("masraf_hesabi", function () {
            return {
                filters: {
                    "is_group": 0,
                    "account_type": "Gider (Expense)"
                }
            };
        });
    }
});
