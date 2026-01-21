// Copyright (c) 2025, Ertu and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stok Duzenleme Fisi', {
    refresh: function (frm) {
        // Fark Hesap Alanını Read-Only yap (Otomatik seçilecek)
        frm.set_df_property('fark_hesabi', 'read_only', 1);
    }
});

frappe.ui.form.on('Stok Duzenleme Kalemi', {
    // Ürün seçildiğinde
    urun: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];

        if (!frm.doc.depo) {
            frappe.msgprint(__("Lütfen önce Depo seçiniz."));
            frappe.model.set_value(cdt, cdn, "urun", "");
            return;
        }

        if (row.urun) {
            // Depodaki Stok bilgisini çek
            frappe.db.get_value('Stok Bakiyesi',
                {
                    'urun': row.urun,
                    'depo': frm.doc.depo
                },
                ['mevcut_miktar', 'birim_maliyet']
            ).then(r => {
                let current_qty = 0;
                let unit_cost = 0;

                if (r && r.message) {
                    current_qty = r.message.mevcut_miktar || 0;
                    unit_cost = r.message.birim_maliyet || 0;
                }

                // Alanları doldur
                frappe.model.set_value(cdt, cdn, 'sistemdeki_stok', current_qty);
                frappe.model.set_value(cdt, cdn, 'degerleme_fiyati', unit_cost);

                // Farkı hesapla (Opsiyonel: Eğer sayım sonucu girilmişse)
                calculate_diff_and_account(frm, cdt, cdn);
            });
        }
    },

    // Sayım Sonucu girildiğinde
    sayim_sonucu: function (frm, cdt, cdn) {
        calculate_diff_and_account(frm, cdt, cdn);
    }
});

function calculate_diff_and_account(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    let sistem = row.sistemdeki_stok || 0;

    if (row.sayim_sonucu === undefined || row.sayim_sonucu === null || row.sayim_sonucu === "") {
        return;
    }

    let sayim = row.sayim_sonucu;
    let fark = sayim - sistem;

    frappe.model.set_value(cdt, cdn, 'fark_miktari', fark);

    // --- Akıllı Hesap Seçimi ---
    // Sadece tek satırda mantık kuruyoruz. Birden fazla satır varsa, son işlem yapılan satırın durumuna göre ana hesap değişir.
    // İdealde Split Entry (Çoklu Hesap) olması gerekir ama basit yapı için Parent'taki tek hesabı yöneteceğiz.
    // Eğer satırlar karışık ise (biri artı, biri eksi), kullanıcıya uyarı vermek lazım ama şimdilik son işleme göre set edelim.

    let target_account_name = "";

    if (fark < 0) {
        // Eksik Var -> Fire
        target_account_name = "Stok Fire ve Zararları";
    } else if (fark > 0) {
        // Fazla Var -> Sayım Fazlası
        target_account_name = "Sayım ve Tesellüm Fazlaları";
    } else {
        // Fark Yok -> Hesap Boşalt
        frm.set_value("fark_hesabi", "");
        return;
    }

    if (target_account_name) {
        frappe.db.get_value("Hesap", { hesap_adi: target_account_name }, "name")
            .then(r => {
                if (r && r.message && r.message.name) {
                    frm.set_value("fark_hesabi", r.message.name);
                }
            });
    }
}
