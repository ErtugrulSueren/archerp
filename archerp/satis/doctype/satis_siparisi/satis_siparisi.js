
// Copyright (c) 2025, Ertu and contributors
// For license information, please see license.txt

frappe.ui.form.on('Satis Siparisi', {
    onload: function (frm) {
        // Otomatik Firma Seçimi
        if (frm.is_new()) {
            frappe.db.get_list('Firma', { fields: ['name'] }).then(records => {
                if (records.length === 1) {
                    frm.set_value('firma', records[0].name);
                }
            });

            // Tarih ve Teslim Tarihi
            if (!frm.doc.tarih) {
                frm.set_value('tarih', frappe.datetime.get_today());
            }
            if (!frm.doc.teslim_tarihi) {
                frm.set_value('teslim_tarihi', frappe.datetime.add_days(frappe.datetime.get_today(), 7));
            }
        }

        // Vergi Şablonu Filtreleme (Sadece Satış)
        frm.set_query("vergi_sablonu", "kalemler", function () {
            return {
                filters: {
                    "vergi_turu": "Satış"
                }
            };
        });

        // Ürün Filtreleme (Sadece Stok Hareketine Uygun Olanlar / Varyantlar)
        frm.set_query("urun", "kalemler", function () {
            return {
                filters: {
                    "has_variants": 0
                }
            };
        });

        // Adres bilgilerini otomatik çek (add_fetch)
        if (cur_frm) {
            cur_frm.add_fetch('fatura_adresi', 'sehir', 'fatura_il');
            cur_frm.add_fetch('fatura_adresi', 'ilce', 'fatura_ilce');
            cur_frm.add_fetch('fatura_adresi', 'acik_adres', 'fatura_acik_adres');

            cur_frm.add_fetch('sevkiyat_adresi', 'sehir', 'sevkiyat_il');
            cur_frm.add_fetch('sevkiyat_adresi', 'ilce', 'sevkiyat_ilce');
            cur_frm.add_fetch('sevkiyat_adresi', 'acik_adres', 'sevkiyat_acik_adres');
        }
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
function calculate_totals(frm) {
    let ara_toplam = 0;
    let vergi_toplami = 0;
    let is_tax_included = frm.doc.vergi_dahil_mi;

    (frm.doc.kalemler || []).forEach(row => {
        let miktar = row.miktar || 0;
        let fiyat = row.birim_fiyat || 0;
        let vergi_orani = row.vergi_orani || 0;

        let ham_tutar = miktar * fiyat;

        let net_tutar = 0;
        let satir_vergi = 0;
        let satir_toplami = 0;

        if (is_tax_included) {
            // Fiyatın içinde vergi var.
            net_tutar = ham_tutar / (1 + (vergi_orani / 100));
            satir_vergi = ham_tutar - net_tutar;
        } else {
            // Fiyat net. Vergi üstüne eklenir.
            net_tutar = ham_tutar;
            satir_vergi = net_tutar * (vergi_orani / 100);
        }

        // Bu sistemde Tutar her zaman Net Tutar olarak kabul ediliyor
        satir_toplami = net_tutar;

        frappe.model.set_value(row.doctype, row.name, 'tutar', satir_toplami);

        ara_toplam += satir_toplami;
        vergi_toplami += satir_vergi;
    });

    let ek_iskonto = frm.doc.ek_iskonto_tutari || 0;

    // Genel Toplam = (Net Toplam + Vergi Toplamı) - İskonto
    let genel_toplam = (ara_toplam + vergi_toplami) - ek_iskonto;

    frm.set_value('ara_toplam', ara_toplam);
    frm.set_value('vergi_toplami', vergi_toplami);
    frm.set_value('genel_toplam', genel_toplam);

    frm.refresh_field('kalemler');
}

frappe.ui.form.on('Siparis Kalemi', {
    urun: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.urun) {
            frappe.db.get_value('Urun', row.urun, ['standart_satis_fiyati', 'urun_adi'])
                .then(r => {
                    if (r && r.message) {
                        frappe.model.set_value(cdt, cdn, 'birim_fiyat', r.message.standart_satis_fiyati || 0);
                        frappe.model.set_value(cdt, cdn, 'urun_adi', r.message.urun_adi); // Opsiyonel
                        calculate_totals(frm);
                    }
                });
        }
    },

    // Vergi Şablonu seçilince Oranı getir
    vergi_sablonu: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.vergi_sablonu) {
            frappe.db.get_value("Vergi", row.vergi_sablonu, "oran")
                .then(r => {
                    let rate = (r && r.message) ? r.message.oran : 0;
                    frappe.model.set_value(cdt, cdn, "vergi_orani", rate);
                    calculate_totals(frm);
                });
        } else {
            frappe.model.set_value(cdt, cdn, "vergi_orani", 0);
            calculate_totals(frm);
        }
    },

    miktar: function (frm, cdt, cdn) { calculate_totals(frm); },
    birim_fiyat: function (frm, cdt, cdn) { calculate_totals(frm); },
    vergi_orani: function (frm, cdt, cdn) { calculate_totals(frm); },

    kalemler_remove: function (frm) { calculate_totals(frm); },
    kalemler_add: function (frm) { calculate_totals(frm); }
});
