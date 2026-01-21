// Copyright (c) 2025, Ertu and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mal Kabul Fisi', {
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

        // 3. Vergi Filtresi
        frm.set_query('vergi_sablonu', 'kalemler', function () {
            return {
                filters: {
                    vergi_turu: 'Alış'
                }
            };
        });

        // 4. Adres Filtreleme (Tedarikçiye göre)
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
    // 1. Yeni Satır Eklendiğinde
    kalemler_add: function (frm, cdt, cdn) {
        // Eğer hedef depo seçiliyse, yeni satıra varsayılan olarak ata
        if (frm.doc.hedef_depo) {
            frappe.model.set_value(cdt, cdn, 'depo', frm.doc.hedef_depo);
        }
        calculate_totals(frm);
    },

    // 2. Ürün Seçildiğinde
    urun: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.urun) return;

        // Ürünün kartındaki varsayılan vergi şablonunu çek
        frappe.db.get_value('Urun', row.urun, ['vergi_sablonu', 'standart_alis_fiyati', 'stok_birimi'])
            .then(r => {
                if (r && r.message) {
                    if (r.message.vergi_sablonu) frappe.model.set_value(cdt, cdn, 'vergi_sablonu', r.message.vergi_sablonu);
                    if (!row.birim_fiyat && r.message.standart_alis_fiyati) frappe.model.set_value(cdt, cdn, 'birim_fiyat', r.message.standart_alis_fiyati);
                    if (r.message.stok_birimi) frappe.model.set_value(cdt, cdn, 'stok_birimi', r.message.stok_birimi);

                    // Close modal after product data loads
                    setTimeout(() => frm.fields_dict.kalemler.grid.grid_form.hide(), 500);
                }
            });
    },

    // 3. Vergi Şablonu Değiştiğinde
    vergi_sablonu: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.vergi_sablonu) {
            frappe.model.set_value(cdt, cdn, 'vergi_orani', 0);
            return;
        }

        // Şablondan 'oran' verisini çek
        frappe.db.get_value('Vergi', row.vergi_sablonu, 'oran')
            .then(r => {
                let rate = 0;
                if (r && r.message && r.message.oran) {
                    rate = r.message.oran;
                }
                frappe.model.set_value(cdt, cdn, 'vergi_orani', rate);
            });
    },

    // 4. Hesaplama Tetikleyicileri
    miktar: function (frm, cdt, cdn) {
        calculate_line_total(frm, cdt, cdn);
        // Immediately close grid form to prevent freeze
        frm.fields_dict.kalemler.grid.grid_form.hide();
    },
    birim_fiyat: function (frm, cdt, cdn) {
        calculate_line_total(frm, cdt, cdn);
        // Immediately close grid form
        frm.fields_dict.kalemler.grid.grid_form.hide();
    },
    vergi_orani: function (frm, cdt, cdn) {
        calculate_line_total(frm, cdt, cdn);
        // Close after tax calculation too
        frm.fields_dict.kalemler.grid.grid_form.hide();
    },
    kalemler_remove: function (frm) { calculate_totals(frm); }
});

// --- HESAPLAMA MOTORU ---

function calculate_line_total(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    let qty = row.miktar || 0;

    let tax_inclusive = frm.doc.vergi_dahil_mi;
    let price = row.birim_fiyat || 0;
    let tax_rate = row.vergi_orani || 0;

    let net_unit_price = 0;

    // Net Fiyat Hesabı
    if (tax_inclusive) {
        // Fiyat = Net * (1 + Oran/100) -> Net = Fiyat / (1 + Oran/100)
        net_unit_price = price / (1 + (tax_rate / 100));
    } else {
        net_unit_price = price;
    }

    // Satır Tutarını yaz (Net Tutar bazlı)
    let amount = qty * net_unit_price;
    frappe.model.set_value(cdt, cdn, 'tutar', amount);

    // Genel Toplamı Güncelle
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

    // 1. Ara Toplam (Net)
    frm.set_value('ara_toplam', total_net);

    // 2. Vergi Toplamı
    frm.set_value('vergi_toplami', total_tax);

    // 3. Genel Toplam (Net + Vergi - İskonto)
    let discount = frm.doc.ek_iskonto_tutari || 0;
    let grand_total = total_net + total_tax - discount;

    if (grand_total < 0) grand_total = 0;

    frm.set_value('genel_toplam', grand_total);
}
