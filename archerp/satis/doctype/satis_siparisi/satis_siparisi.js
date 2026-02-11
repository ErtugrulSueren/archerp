
// Copyright (c) 2025, Ertu and contributors
// For license information, please see license.txt

frappe.ui.form.on('Satis Siparisi', {
    onload: function (frm) {





    },

    refresh: function (frm) {
        // per_delivered alanı olmadığı için status alanına göre kontrol ediyoruz
        // Tamamlandı veya İptal DEĞİLSE ve Onaylıysa
        if (frm.doc.docstatus === 1 && frm.doc.status !== 'Tamamlandı' && frm.doc.status !== 'İptal') {
            frm.add_custom_button(__('İrsaliye Oluştur'), function () {
                frappe.model.open_mapped_doc({
                    method: "archerp.satis.doctype.satis_siparisi.satis_siparisi.make_delivery_note",
                    frm: frm
                });
            }, __('Oluştur'));
        }
    },

    // Vergi Dahil/Hariç değiştiğinde hesapla
    vergi_dahil_mi: function (frm) {
        calculate_totals(frm);
    },

    ek_iskonto_tutari: function (frm) {
        calculate_totals(frm);
    }
});

// ---------------------------------------------------------
// Hesaplamalar (Gelişmiş Vergi Motoru)
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
                // Gelen verideki satırları mevcut form satırlarıyla eşleştir
                if (d.kalemler && d.kalemler.length > 0) {
                    d.kalemler.forEach(function (row) {
                        // Formdaki satırı bul (name üzerinden)
                        let form_row = (frm.doc.kalemler || []).find(fr => fr.name === row.name);
                        if (form_row) {
                            // Model Set Value kullanarak UI tetiklenmesini sağla
                            frappe.model.set_value(form_row.doctype, form_row.name, 'tutar', row.tutar);
                            // İskonto veya diğer değişenler varsa onları da ekleyebiliriz
                            if (row.muhasebe_hesabi) frappe.model.set_value(form_row.doctype, form_row.name, 'muhasebe_hesabi', row.muhasebe_hesabi);
                        }
                    });
                }

                frm.refresh_fields();
            }
        }
    });
}

// Eski calculate_line_total fonksiyonuna ihtiyaç kalmadı, direkt calculate_totals çağıracağız.
function calculate_line_total(frm, cdt, cdn) {
    calculate_totals(frm);
}

frappe.ui.form.on('Siparis Kalemi', {
    miktar: function (frm, cdt, cdn) { calculate_totals(frm); },
    birim_fiyat: function (frm, cdt, cdn) { calculate_totals(frm); },
    vergi_orani: function (frm, cdt, cdn) { calculate_totals(frm); },

    kalemler_remove: function (frm) { calculate_totals(frm); },
    kalemler_add: function (frm) { calculate_totals(frm); }
});
