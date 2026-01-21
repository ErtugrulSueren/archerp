// Copyright (c) 2025, Ertu and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sevk Irsaliyesi', {
    onload: function (frm) {
        // Otomatik Firma Seçimi
        if (frm.is_new()) {
            frappe.db.get_list('Firma', { fields: ['name'] }).then(records => {
                if (records.length === 1) {
                    frm.set_value('firma', records[0].name);
                }
            });
        }

        // Vergi Şablonu Filtreleme (Sadece Satış)
        frm.set_query("vergi_sablonu", "kalemler", function () {
            return {
                filters: {
                    "vergi_turu": "Satış"
                }
            };
        });

        // Ürün Filtreleme (Sadece Stok Hareketine Uygun Olanlar)
        frm.set_query("urun", "kalemler", function () {
            return {
                filters: {
                    "has_variants": 0
                }
            };
        });
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

    // Müşteri seçildiğinde Adresleri getir
    musteri: function (frm) {
        if (!frm.doc.musteri) {
            frm.set_df_property('sevk_adresi', 'options', []);
            frm.set_value('sevk_adresi', '');
            frm.set_value('acik_adres', '');
            frm.set_value('sehir', '');
            frm.set_value('ilce', '');
            return;
        }

        frappe.call({
            method: 'frappe.client.get',
            args: {
                doctype: 'Musteri',
                name: frm.doc.musteri
            },
            callback: function (r) {
                if (r.message) {
                    let musteri = r.message;
                    let adresler = musteri.adresler || [];
                    let options = [""];
                    adresler.forEach(function (addr) {
                        if (addr.title) {
                            options.push(addr.title);
                        }
                    });
                    frm.set_df_property('sevk_adresi', 'options', options);

                    if (options.length === 2) {
                        frm.set_value('sevk_adresi', options[1]);
                    }
                }
            }
        });
    },

    // Adres Başlığı seçildiğinde detayları doldur
    sevk_adresi: function (frm) {
        let secilen_baslik = frm.doc.sevk_adresi;
        if (!secilen_baslik) {
            frm.set_value('acik_adres', '');
            frm.set_value('sehir', '');
            frm.set_value('ilce', '');
            return;
        }

        if (frm.doc.musteri) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Musteri',
                    name: frm.doc.musteri
                },
                callback: function (r) {
                    if (r.message && r.message.adresler) {
                        let adres = r.message.adresler.find(a => a.title === secilen_baslik);
                        if (adres) {
                            frm.set_value('acik_adres', adres.acik_adres);
                            frm.set_value('sehir', adres.sehir);
                            frm.set_value('ilce', adres.ilce);
                        }
                    }
                }
            });
        }
    }
});

function update_depo_label(frm) {
    let label = frm.doc.iade_mi ? "Giriş Deposu" : "Çıkış Deposu";
    if (frm.fields_dict['kalemler'] && frm.fields_dict['kalemler'].grid) {
        frm.fields_dict['kalemler'].grid.update_docfield_property('depo', 'label', label);
    }
}

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
        let satir_toplami = 0; // Gridde 'tutar' alanına yazılacak (Genelde Net + Vergi mi yoksa sadece Net mi olduğu ERP tercihine bağlı ama ArchERP'de genelde Tutar = Net Tutar * Miktar gibi olabilir, ama burada Kullanıcı "Tutar (Satır Toplamı) = net_tutar" demiş (Senaryo A). Ve Senaryo B'de de net_tutar. 
        // Bekle, user request:
        // A (Dahil): tutar = net_tutar
        // B (Hariç): tutar = net_tutar
        // Yani 'tutar' kolonu her zaman NET TUTAR (Vergisiz) anlamına geliyor gibi görünüyor isteğe göre?
        // KONTROL: "tutar (Satır Toplamı) = net_tutar" (Senaryo A). "tutar (Satır Toplamı) = net_tutar" (Senaryo B).
        // Bu durumda 'ara_toplam' da netlerin toplamı.
        // O zaman Genel Toplam = Net Toplam + Vergi Toplamı mantığı oturur.
        // Ancak genelde 'Row Total' miktar * birim fiyat olur.
        // User isteğine sadık kalacağım: "tutar = net_tutar".

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

        satir_toplami = net_tutar;

        // Satır Tutarını Güncelle (Net Tutar olarak)
        frappe.model.set_value(row.doctype, row.name, 'tutar', satir_toplami);

        ara_toplam += satir_toplami;
        vergi_toplami += satir_vergi;
    });

    let ek_iskonto = frm.doc.ek_iskonto_tutari || 0;

    // Genel Toplam = (Net Toplam + Vergi Toplamı) - İskonto
    // Not: İskonto vergi öncesi mi sonrası mı? User formül: "genel_toplam = (ara_toplam + vergi_toplami) - ek_iskonto_tutari". 
    // Yani toplamdan düşüyor.
    let genel_toplam = (ara_toplam + vergi_toplami) - ek_iskonto;

    frm.set_value('ara_toplam', ara_toplam);
    frm.set_value('vergi_toplami', vergi_toplami);
    frm.set_value('genel_toplam', genel_toplam);

    frm.refresh_field('kalemler');
}

frappe.ui.form.on('Teslimat Kalemi', {
    urun: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.urun) {
            frappe.db.get_value('Urun', row.urun, ['standart_satis_fiyati', 'stok_birimi'])
                .then(r => {
                    if (r && r.message) {
                        frappe.model.set_value(cdt, cdn, 'birim_fiyat', r.message.standart_satis_fiyati || 0);
                        if (r.message.stok_birimi) {
                            frappe.model.set_value(cdt, cdn, 'stok_birimi', r.message.stok_birimi);
                        }
                        // Note: calculate_totals will trigger via birim_fiyat change or manually call if needed, but set_value usually triggers change event if field is on form? No, JS set_value doesn't trigger on_change unless explicit.
                        calculate_totals(frm);
                    }
                });

            if (row.depo) {
                fetch_cost(frm, cdt, cdn);
            }
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

    depo: function (frm, cdt, cdn) {
        fetch_cost(frm, cdt, cdn);
    },

    miktar: function (frm, cdt, cdn) { calculate_totals(frm); },
    birim_fiyat: function (frm, cdt, cdn) { calculate_totals(frm); },
    vergi_orani: function (frm, cdt, cdn) { calculate_totals(frm); },

    kalemler_remove: function (frm) { calculate_totals(frm); },
    kalemler_add: function (frm) { calculate_totals(frm); }
});

function fetch_cost(frm, cdt, cdn) {
    var row = locals[cdt][cdn];
    if (row.urun && row.depo) {
        frappe.db.get_value('Stok Bakiyesi',
            { 'urun': row.urun, 'depo': row.depo },
            'birim_maliyet'
        ).then(r => {
            let cost = (r && r.message && r.message.birim_maliyet) ? r.message.birim_maliyet : 0;
            frappe.model.set_value(cdt, cdn, 'birim_maliyet', cost);
        });
    }
}
