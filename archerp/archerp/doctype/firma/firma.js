frappe.ui.form.on("Firma", {
    refresh(frm) {
        // 1. Stok Hesabı Filtresi (Varlık/Stok)
        frm.set_query("varsayilan_stok_hesabi", function () {
            return {
                "filters": {
                    "is_group": 0,
                    "account_type": "Stok (Stock)"
                }
            };
        });

        // 2. SMM Hesabı Filtresi (Gider)
        frm.set_query("smm_hesabi", function () {
            return {
                "filters": {
                    "is_group": 0,
                    "account_type": "Gider (Expense)"
                }
            };
        });

        // 3. Mal Kabul Hesabı Filtresi (Yükümlülük)
        frm.set_query("mal_kabul_hesabi", function () {
            return {
                "filters": {
                    "is_group": 0,
                    "account_type": "Yükümlülük (Liability)"
                }
            };
        });

        // Auto-Set Logic
        if (!frm.doc.varsayilan_stok_hesabi) auto_set_account(frm, "varsayilan_stok_hesabi", { "is_group": 0, "account_type": "Stok (Stock)" });
        if (!frm.doc.smm_hesabi) auto_set_account(frm, "smm_hesabi", { "is_group": 0, "account_type": "Gider (Expense)" });
        if (!frm.doc.mal_kabul_hesabi) auto_set_account(frm, "mal_kabul_hesabi", { "is_group": 0, "account_type": "Yükümlülük (Liability)" });
    }
});

function auto_set_account(frm, field, filters) {
    frappe.db.get_list('Hesap', {
        filters: filters,
        limit: 2
    }).then(r => {
        if (r.length === 1) {
            frm.set_value(field, r[0].name);
        }
    });
}
