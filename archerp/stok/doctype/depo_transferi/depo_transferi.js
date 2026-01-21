// Copyright (c) 2025, Ertu and contributors
// For license information, please see license.txt

frappe.ui.form.on('Depo Transferi', {
    refresh: function (frm) {

    },

    kaynak_depo: function (frm) {
        if (frm.doc.kaynak_depo && frm.doc.hedef_depo) {
            if (frm.doc.kaynak_depo == frm.doc.hedef_depo) {
                frappe.msgprint(__("Kaynak ve Hedef depo aynı olamaz!"));
                frm.set_value("kaynak_depo", "");
            }
        }
    },

    hedef_depo: function (frm) {
        if (frm.doc.kaynak_depo && frm.doc.hedef_depo) {
            if (frm.doc.kaynak_depo == frm.doc.hedef_depo) {
                frappe.msgprint(__("Kaynak ve Hedef depo aynı olamaz!"));
                frm.set_value("hedef_depo", "");
            }
        }
    }
});

frappe.ui.form.on('Depo Transfer Kalemi', {
    // Ürün seçildiğinde
    urun: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];

        if (!frm.doc.kaynak_depo) {
            frappe.msgprint(__("Lütfen önce Kaynak Depo seçiniz."));
            frappe.model.set_value(cdt, cdn, "urun", "");
            return;
        }

        if (row.urun) {
            // Kaynak Depodaki Stok bilgisini çek
            frappe.db.get_value('Stok Bakiyesi',
                {
                    'urun': row.urun,
                    'depo': frm.doc.kaynak_depo
                },
                ['mevcut_miktar', 'birim_maliyet']
            ).then(r => {
                let current_qty = 0;
                let unit_cost = 0;

                if (r && r.message) {
                    current_qty = r.message.mevcut_miktar || 0;
                    unit_cost = r.message.birim_maliyet || 0;
                }

                // Maliyet bilgisini satıra taşı
                frappe.model.set_value(cdt, cdn, 'birim_maliyet', unit_cost);

                // Mevcut stoğu satırda saklayalım (Hidden/Virtual) - Validasyon için
                row._mevcut_stok = current_qty;

                // Kullanıcıya bilgi verelim (Toast message)
                frappe.show_alert({
                    message: __("Kaynak Depo Stoğu: {0}", [current_qty]),
                    indicator: 'blue'
                }, 3);
            });
        }
    },

    // Miktar kontrolü
    transfer_miktari: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];

        // Eğer _mevcut_stok undefined ise (henüz fetch bitmediyse veya refresh sonrası) tekrar çekmek gerekebilir
        // Ama basitlik için varsa kontrol edelim
        if (row._mevcut_stok !== undefined) {
            if (row.transfer_miktari > row._mevcut_stok) {
                frappe.msgprint({
                    title: __('Yetersiz Stok'),
                    message: __('Dikkat: Transfer miktarı ({0}), kaynak depodaki stoktan ({1}) fazla.', [row.transfer_miktari, row._mevcut_stok]),
                    indicator: 'orange' // Sarı uyarı, engelleme server side
                });
            }
        }
    }
});
