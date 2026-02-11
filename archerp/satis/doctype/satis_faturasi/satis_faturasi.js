
// Copyright (c) 2025, Ertu and contributors
// For license information, please see license.txt

frappe.ui.form.on('Satis Faturasi', {
    onload: function (frm) {
    },

    refresh: function (frm) {
        if (frm.doc.docstatus === 1 && frm.doc.status !== 'Ödendi') {
            frm.add_custom_button(__('Ödeme Al'), function () {
                var kalan_tutar = flt(frm.doc.genel_toplam) - flt(frm.doc.odenen_tutar);
                if (kalan_tutar < 0) kalan_tutar = 0;

                frappe.new_doc('Odeme Islemi', {
                    odeme_turu: "Tahsilat(Al)",
                    taraf_tipi: "Musteri",
                    taraf_kisi: frm.doc.musteri,
                    odenen_tutar: kalan_tutar,
                    referans_tipi: "Satis Faturasi",
                    referans_no: frm.doc.name,
                    aciklama: "Fatura Tahsilatı: " + frm.doc.name
                });
            }, __('Oluştur'));
        }
    },

    odeme_kosulu: function (frm) {
        if (frm.doc.odeme_kosulu) {
            frappe.db.get_value("Odeme Kosulu", frm.doc.odeme_kosulu, "vade_gun_sayisi")
                .then(r => {
                    if (r && r.message) {
                        let days = r.message.vade_gun_sayisi || 0;
                        let invoice_date = frm.doc.fatura_tarihi || frappe.datetime.get_today();
                        let due_date = frappe.datetime.add_days(invoice_date, days);
                        frm.set_value("vade_tarihi", due_date);
                    }
                });
        }
    },

    // Müşteri seçince adresleri güncelle
    musteri: function (frm) {
        if (frm.doc.musteri) {
            // Opsiyonel: Müşterinin varsayılan adresini çekebiliriz
        }
    },

    vergi_dahil_mi: function (frm) {
        calculate_totals(frm);
    },

    ek_iskonto_tutari: function (frm) {
        calculate_totals(frm);
    }
});

// ---------------------------------------------------------
// Hesaplamalar
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

function calculate_line_total(frm, cdt, cdn) {
    calculate_totals(frm);
}

frappe.ui.form.on('Fatura Kalemi', {
    miktar: function (frm, cdt, cdn) { calculate_totals(frm); },
    birim_fiyat: function (frm, cdt, cdn) { calculate_totals(frm); },
    vergi_orani: function (frm, cdt, cdn) { calculate_totals(frm); },

    kalemler_remove: function (frm) { calculate_totals(frm); }
});
