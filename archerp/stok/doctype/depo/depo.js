frappe.ui.form.on("Depo", {
    refresh(frm) {
        // Stok Hesabı Filtresi (Varlık/Stok)
        frm.set_query("stok_hesabi", function () {
            return {
                "filters": {
                    "is_group": 0,
                    "account_type": "Stok (Stock)"
                }
            };
        });

        // Auto-Set Logic
        if (!frm.doc.stok_hesabi) {
            frappe.db.get_list('Hesap', {
                filters: { "is_group": 0, "account_type": "Stok (Stock)" },
                limit: 2
            }).then(r => {
                if (r.length === 1) {
                    frm.set_value("stok_hesabi", r[0].name);
                }
            });
        }
    }
});
