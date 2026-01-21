// Copyright (c) 2025, Ertu and contributors
// For license information, please see license.txt

frappe.ui.form.on('Satis Teklifi', {
    onload: function (frm) {
        // Otomatik Firma Seçimi
        if (frm.is_new()) {
            frappe.db.get_list('Firma', { fields: ['name'] }).then(records => {
                if (records.length === 1) {
                    frm.set_value('firma', records[0].name);
                }
            });
        }

        // Varsayılan Geçerlilik Tarihi (Bugün + 30 Gün)
        if (frm.is_new() && !frm.doc.gercerlilik_tarihi) {
            let today = frappe.datetime.get_today();
            let valid_until = frappe.datetime.add_days(today, 30);
            frm.set_value('gercerlilik_tarihi', valid_until);
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

        // Adres Filtreleme (Müşteriye göre)
        // Adres Detayi, Musteri'nin child table'ı (adresler). Parent = Musteri Name.
        frm.set_query("fatura_adresi", function () {
            return {
                filters: {
                    "parent": frm.doc.musteri,
                    "parenttype": "Musteri"
                }
            };
        });

        frm.set_query("sevkiyat_adresi", function () {
            return {
                filters: {
                    "parent": frm.doc.musteri,
                    "parenttype": "Musteri"
                }
            };
        });
    },

    // Fatura Adresi değişince detayları çek
    fatura_adresi: function (frm) {
        if (frm.doc.fatura_adresi) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Adres Detayi',
                    name: frm.doc.fatura_adresi
                },
                callback: function (r) {
                    if (r && r.message) {
                        frm.set_value('il', r.message.sehir);
                        frm.set_value('ilce', r.message.ilce);
                        frm.set_value('acik_adres', r.message.acik_adres);
                    }
                }
            });
        } else {
            frm.set_value('il', '');
            frm.set_value('ilce', '');
            frm.set_value('acik_adres', '');
        }
    },

    // Sevkiyat Adresi değişince detayları çek
    sevkiyat_adresi: function (frm) {
        if (frm.doc.sevkiyat_adresi) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Adres Detayi',
                    name: frm.doc.sevkiyat_adresi
                },
                callback: function (r) {
                    if (r && r.message) {
                        frm.set_value('sevkiyat_il', r.message.sehir);
                        frm.set_value('sevkiyat_ilce', r.message.ilce);
                        frm.set_value('sevkiyat_acik_adres', r.message.acik_adres);
                    }
                }
            });
        } else {
            frm.set_value('sevkiyat_il', '');
            frm.set_value('sevkiyat_ilce', '');
            frm.set_value('sevkiyat_acik_adres', '');
        }
    },

    refresh: function (frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Sipariş Oluştur'), function () {
                frappe.model.open_mapped_doc({
                    method: "archerp.satis.doctype.satis_teklifi.satis_teklifi.make_sales_order",
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
    },

    // Müşteri para birimi v.s. seçince kur gelebilir ama şimdilik manuel tetikleme eklemeye gerek yok.
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
        let fiyat = row.birim_fiyat || 0; // Eğer vergi dahilse bu brüt, hariçse net fiyattır.
        let vergi_orani = row.vergi_orani || 0;

        let ham_tutar = miktar * fiyat;

        let net_tutar = 0;
        let satir_vergi = 0;
        let satir_toplami = 0;

        if (is_tax_included) {
            // Fiyatın içinde vergi var.
            // Net = Ham / (1 + rate/100)
            net_tutar = ham_tutar / (1 + (vergi_orani / 100));
            satir_vergi = ham_tutar - net_tutar;
        } else {
            // Fiyat net. Vergi üstüne eklenir.
            net_tutar = ham_tutar;
            satir_vergi = net_tutar * (vergi_orani / 100);
        }

        // Bu sistemde Tutar her zaman Net Tutar olarak kabul ediliyor (İrsaliye ile uyumlu)
        satir_toplami = net_tutar;

        // Satır Tutarını Güncelle
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

frappe.ui.form.on('Satis Kalemi', {
    urun: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.urun) {
            frappe.db.get_value('Urun', row.urun, ['standart_satis_fiyati', 'urun_adi'])
                .then(r => {
                    if (r && r.message) {
                        frappe.model.set_value(cdt, cdn, 'birim_fiyat', r.message.standart_satis_fiyati || 0);
                        // İsteğe bağlı: Ürün adını açıklama alanına da basabiliriz ama şimdilik gerek yok.
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
