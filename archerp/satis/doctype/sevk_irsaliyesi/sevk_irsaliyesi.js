// Copyright (c) 2025, Ertu and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sevk Irsaliyesi', {
    onload: function (frm) {
    },

    refresh: function (frm) {
        update_depo_label(frm);

        if (frm.doc.docstatus === 1 && frm.doc.status !== 'İptal' && frm.doc.status !== 'İade' && frm.doc.status !== 'Tamamlandı') {
            frm.add_custom_button(__('Fatura Oluştur'), function () {
                frappe.model.open_mapped_doc({
                    method: "archerp.satis.doctype.sevk_irsaliyesi.sevk_irsaliyesi.make_sales_invoice",
                    frm: frm
                });
            }, __('Oluştur'));
        }
    },

    iade_mi: function (frm) {
        update_depo_label(frm);
    },

    // Vergi Dahil/Hariç değiştiğinde hesapla
    vergi_dahil_mi: function (frm) {
        calculate_totals(frm);
    },

    ek_iskonto_tutari: function (frm) {
        calculate_totals(frm);
    },


});

function update_depo_label(frm) {
    let label = frm.doc.iade_mi ? "Giriş Deposu" : "Çıkış Deposu";
    if (frm.fields_dict['kalemler'] && frm.fields_dict['kalemler'].grid) {
        frm.fields_dict['kalemler'].grid.update_docfield_property('depo', 'label', label);
    }
}

// ---------------------------------------------------------
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
                if (d.base_genel_toplam) frm.set_value('base_genel_toplam', d.base_genel_toplam);

                // 2. Satır Tutarlarını Güncelle
                if (d.kalemler && d.kalemler.length > 0) {
                    d.kalemler.forEach(function (row) {
                        let form_row = (frm.doc.kalemler || []).find(fr => fr.name === row.name);
                        if (form_row) {
                            frappe.model.set_value(form_row.doctype, form_row.name, 'tutar', row.tutar);
                            if (row.muhasebe_hesabi) frappe.model.set_value(form_row.doctype, form_row.name, 'muhasebe_hesabi', row.muhasebe_hesabi);
                        }
                    });
                }

                frm.refresh_fields();
            }
        }
    });
}

frappe.ui.form.on('Teslimat Kalemi', {
    miktar: function (frm, cdt, cdn) { calculate_totals(frm); },
    birim_fiyat: function (frm, cdt, cdn) { calculate_totals(frm); },
    vergi_orani: function (frm, cdt, cdn) { calculate_totals(frm); },

    kalemler_remove: function (frm) { calculate_totals(frm); },
    kalemler_add: function (frm) { calculate_totals(frm); }
});
