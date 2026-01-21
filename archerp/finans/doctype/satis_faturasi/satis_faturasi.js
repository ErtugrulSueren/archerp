
// Copyright (c) 2025, Ertu and contributors
// For license information, please see license.txt

frappe.ui.form.on('Satis Faturasi', {
    onload: function (frm) {
        // Otomatik Firma Seçimi
        if (frm.is_new()) {
            frappe.db.get_list('Firma', { fields: ['name'] }).then(records => {
                if (records.length === 1) {
                    frm.set_value('firma', records[0].name);
                }
            });

            if (!frm.doc.fatura_tarihi) {
                frm.set_value('fatura_tarihi', frappe.datetime.get_today());
            }

            // Borç Hesabı Otomatik Seçimi
            if (!frm.doc.borc_hesabi) {
                frappe.db.get_value("Hesap", { "hesap_adi": "Muhtelif Alıcılar" }, "name")
                    .then(r => {
                        if (r && r.message) {
                            frm.set_value("borc_hesabi", r.message.name);
                        }
                    });
            }
        }

        // Adres bilgilerini otomatik çek (add_fetch)
        if (cur_frm) {
            cur_frm.add_fetch('fatura_adresi', 'sehir', 'fatura_il');
            cur_frm.add_fetch('fatura_adresi', 'ilce', 'fatura_ilce');
            cur_frm.add_fetch('fatura_adresi', 'acik_adres', 'fatura_acik_adres');

            cur_frm.add_fetch('sevkiyat_adresi', 'sehir', 'sevkiyat_il');
            cur_frm.add_fetch('sevkiyat_adresi', 'ilce', 'sevkiyat_ilce');
            cur_frm.add_fetch('sevkiyat_adresi', 'acik_adres', 'sevkiyat_acik_adres');
        }

        // Vergi Şablonu Filtreleme
        frm.set_query("vergi_sablonu", "kalemler", function () {
            return {
                filters: {
                    "vergi_turu": "Satış"
                }
            };
        });

        // Ürün Filtreleme (Varyant)
        frm.set_query("urun", "kalemler", function () {
            return {
                filters: {
                    "has_variants": 0
                }
            };
        });
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

        satir_toplami = net_tutar; // Tutar alanına Net Tutar yazıyoruz

        frappe.model.set_value(row.doctype, row.name, 'tutar', satir_toplami);

        ara_toplam += satir_toplami;
        vergi_toplami += satir_vergi;
    });

    let ek_iskonto = frm.doc.ek_iskonto_tutari || 0;
    let genel_toplam = (ara_toplam + vergi_toplami) - ek_iskonto;

    frm.set_value('ara_toplam', ara_toplam);
    frm.set_value('vergi_toplami', vergi_toplami);
    frm.set_value('genel_toplam', genel_toplam);

    frm.refresh_field('kalemler');
}

frappe.ui.form.on('Fatura Kalemi', {
    kalemler_add: function (frm, cdt, cdn) {
        // Yeni satır eklendiğinde Gelir Hesabını otomatik getir
        frappe.db.get_value("Hesap", { "hesap_adi": "Yurtiçi Satışlar" }, "name")
            .then(r => {
                if (r && r.message) {
                    frappe.model.set_value(cdt, cdn, "gelir_hesabi", r.message.name);
                }
            });
    },

    urun: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.urun) {
            frappe.db.get_value('Urun', row.urun, ['standart_satis_fiyati', 'stok_birimi'])
                .then(r => {
                    if (r && r.message) {
                        frappe.model.set_value(cdt, cdn, 'birim_fiyat', r.message.standart_satis_fiyati || 0);
                        frappe.model.set_value(cdt, cdn, 'stok_birimi', r.message.stok_birimi);
                        calculate_totals(frm);
                    }
                });
        }
    },

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

    kalemler_remove: function (frm) { calculate_totals(frm); }
});
