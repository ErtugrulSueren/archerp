// Copyright (c) 2025, Ertu and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mal Kabul Fisi', {
    onload: function (frm) {
    },

    refresh: function (frm) {
        // 4. Hesaplamaları Tetikle (Görünürlük için)
        if (!frm.doc.__islocal && frm.doc.docstatus === 0) {
            calculate_totals(frm);
        }

        if (frm.doc.docstatus === 1 && frm.doc.status !== "Tamamlandı" && frm.doc.status !== "İptal" && frm.doc.status !== "İade") {
            frm.add_custom_button(__('Satın Alma Faturası Oluştur'), function () {
                frappe.model.open_mapped_doc({
                    method: "archerp.stok.doctype.mal_kabul_fisi.mal_kabul_fisi.make_purchase_invoice",
                    frm: frm
                })
            }, __('Oluştur'));
        }
    },

    // Global Tetikleyiciler
    vergi_dahil_mi: function (frm) { calculate_totals(frm); },
    ek_iskonto_tutari: function (frm) { calculate_totals(frm); }
});

frappe.ui.form.on('Mal Kabul Kalemi', {
    kalemler_add: function (frm, cdt, cdn) {
        if (frm.doc.hedef_depo) {
            frappe.model.set_value(cdt, cdn, 'depo', frm.doc.hedef_depo);
        }
        calculate_totals(frm);
    },
    miktar: function (frm, cdt, cdn) { calculate_totals(frm); },
    birim_fiyat: function (frm, cdt, cdn) { calculate_totals(frm); },
    vergi_orani: function (frm, cdt, cdn) { calculate_totals(frm); },
    kalemler_remove: function (frm) { calculate_totals(frm); }
});

// --- HESAPLAMA MOTORU ---

// ---------------------------------------------------------
// Hesaplamalar (API / Controller Üzerinden)
// ---------------------------------------------------------
function calculate_totals(frm) {
    if (!frm.doc.kalemler || frm.doc.kalemler.length === 0) return;

    frappe.call({
        method: "archerp.controllers.transaction_controller.calculate_doc",
        args: {
            doc: frm.doc
        },
        callback: function (r) {
            if (r.message) {
                let d = r.message;

                // 1. Ana Toplamlar
                frm.set_value('ara_toplam', d.ara_toplam);
                frm.set_value('vergi_toplami', d.vergi_toplami);
                frm.set_value('genel_toplam', d.genel_toplam);

                // 2. Satır Tutarlarını Güncelle
                if (d.kalemler && d.kalemler.length > 0) {
                    d.kalemler.forEach(function (row) {
                        let form_row = (frm.doc.kalemler || []).find(fr => fr.name === row.name);
                        if (form_row) {
                            frappe.model.set_value(form_row.doctype, form_row.name, 'tutar', row.tutar);
                        }
                    });
                }

                frm.refresh_fields();
            }
        }
    });
}
