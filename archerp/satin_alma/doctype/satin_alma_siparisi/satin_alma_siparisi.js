frappe.ui.form.on('Satin Alma Siparisi', {
    onload: function (frm) {
    },


    refresh: function (frm) {
        // 3. Hesaplamaları Tetikle
        if (!frm.doc.__islocal && frm.doc.docstatus === 0) {
            calculate_totals(frm);
        }

        if (frm.doc.docstatus === 1 && frm.doc.status !== "Tamamlandı" && frm.doc.status !== "İptal" && frm.doc.status !== "Kapatıldı") {
            frm.add_custom_button(__('Mal Kabul Oluştur'), function () {
                frappe.model.open_mapped_doc({
                    method: "archerp.satin_alma.doctype.satin_alma_siparisi.satin_alma_siparisi.make_mal_kabul_fisi",
                    frm: frm
                })
            }, __('Oluştur'));
        }
    },
    vergi_dahil_mi: function (frm) { calculate_totals(frm); },
    ek_iskonto_tutari: function (frm) { calculate_totals(frm); },
    para_birimi: function (frm) {
        if (frm.doc.para_birimi == frappe.get_doc(":Company", frm.doc.firma).default_currency) {
            frm.set_value('doviz_kuru', 1.0);
        }
    }
});

frappe.ui.form.on('Satin Alma Kalemi', {
    kalemler_remove: function (frm) { calculate_totals(frm); },
    miktar: function (frm, cdt, cdn) { calculate_line_total(frm, cdt, cdn); },
    birim_fiyat: function (frm, cdt, cdn) { calculate_line_total(frm, cdt, cdn); },
    vergi_orani: function (frm, cdt, cdn) { calculate_line_total(frm, cdt, cdn); }
});



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

function calculate_line_total(frm, cdt, cdn) {
    calculate_totals(frm);
}
