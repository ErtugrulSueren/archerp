frappe.ui.form.on('Satin Alma Siparisi', {
    onload: function (frm) {
        // 1. Tek Firma Varsa Otomatik Seç
        if (frm.is_new() && !frm.doc.firma) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Firma",
                    fields: ["name"],
                    limit_page_length: 2
                },
                callback: function (r) {
                    if (r.message && r.message.length === 1) {
                        frm.set_value('firma', r.message[0].name);
                    }
                }
            });
        }

        // 2. Ürün Filtresi
        frm.set_query("urun", "kalemler", function () {
            return {
                filters: {
                    "has_variants": 0
                }
            };
        });

        // 3. Adres Filtreleme (Tedarikçiye göre)
        frm.set_query("fatura_adresi", function () {
            return {
                filters: {
                    "parent": frm.doc.tedarikci,
                    "parenttype": "Tedarikci"
                }
            };
        });

        frm.set_query("teslimat_adresi", function () {
            return {
                filters: {
                    "parent": frm.doc.tedarikci,
                    "parenttype": "Tedarikci"
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
                        frm.set_value('fatura_il', r.message.sehir);
                        frm.set_value('fatura_ilce', r.message.ilce);
                        frm.set_value('fatura_acik_adres', r.message.acik_adres);
                    }
                }
            });
        } else {
            frm.set_value('fatura_il', '');
            frm.set_value('fatura_ilce', '');
            frm.set_value('fatura_acik_adres', '');
        }
    },

    // Teslimat Adresi değişince detayları çek
    teslimat_adresi: function (frm) {
        if (frm.doc.teslimat_adresi) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Adres Detayi',
                    name: frm.doc.teslimat_adresi
                },
                callback: function (r) {
                    if (r && r.message) {
                        frm.set_value('teslimat_il', r.message.sehir);
                        frm.set_value('teslimat_ilce', r.message.ilce);
                        frm.set_value('teslimat_acik_adres', r.message.acik_adres);
                    }
                }
            });
        } else {
            frm.set_value('teslimat_il', '');
            frm.set_value('teslimat_ilce', '');
            frm.set_value('teslimat_acik_adres', '');
        }
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
    urun: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.urun) return;
        frappe.db.get_value('Urun', row.urun, ['standart_alis_fiyati', 'vergi_sablonu', 'stok_birimi', 'gider_hesabi'])
            .then(r => {
                if (r && r.message) {
                    if (!row.birim_fiyat) frappe.model.set_value(cdt, cdn, 'birim_fiyat', r.message.standart_alis_fiyati);
                    if (r.message.vergi_sablonu) frappe.model.set_value(cdt, cdn, 'vergi_sablonu', r.message.vergi_sablonu);
                    if (r.message.stok_birimi) frappe.model.set_value(cdt, cdn, 'stok_birimi', r.message.stok_birimi);
                    if (r.message.gider_hesabi) frappe.model.set_value(cdt, cdn, 'gider_hesabi', r.message.gider_hesabi);
                }
            });
    },
    vergi_sablonu: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.vergi_sablonu) {
            frappe.model.set_value(cdt, cdn, 'vergi_orani', 0);
            return;
        }
        frappe.db.get_value('Vergi', row.vergi_sablonu, 'oran')
            .then(r => {
                if (r && r.message) {
                    frappe.model.set_value(cdt, cdn, 'vergi_orani', r.message.oran);
                }
            });
    },
    vergi_orani: function (frm, cdt, cdn) { calculate_line_total(frm, cdt, cdn); }
});

function calculate_line_total(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    let qty = row.miktar || 0;
    let price = row.birim_fiyat || 0;
    let tax_rate = row.vergi_orani || 0;
    let tax_inclusive = frm.doc.vergi_dahil_mi;
    let net_unit_price = 0;

    if (tax_inclusive) {
        net_unit_price = price / (1 + (tax_rate / 100));
    } else {
        net_unit_price = price;
    }

    let amount = qty * net_unit_price;
    frappe.model.set_value(cdt, cdn, 'tutar', amount);
    calculate_totals(frm);
}

function calculate_totals(frm) {
    let total_net = 0;
    let total_tax = 0;
    let tax_inclusive = frm.doc.vergi_dahil_mi;

    (frm.doc.kalemler || []).forEach(function (row) {
        let qty = row.miktar || 0;
        let price = row.birim_fiyat || 0;
        let tax_rate = row.vergi_orani || 0;
        let net_unit_price = 0;
        let unit_tax = 0;

        if (tax_inclusive) {
            net_unit_price = price / (1 + (tax_rate / 100));
            unit_tax = price - net_unit_price;
        } else {
            net_unit_price = price;
            unit_tax = net_unit_price * (tax_rate / 100);
        }

        total_net += qty * net_unit_price;
        total_tax += qty * unit_tax;
    });

    frm.set_value('ara_toplam', total_net);
    frm.set_value('vergi_toplami', total_tax);
    let discount = frm.doc.ek_iskonto_tutari || 0;
    let grand_total = total_net + total_tax - discount;
    if (grand_total < 0) grand_total = 0;
    frm.set_value('genel_toplam', grand_total);
}
