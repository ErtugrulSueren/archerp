// Copyright (c) 2025, Ertu and contributors
// For license information, please see license.txt

const HESAP_ESLESMELERI = {
    "Fire / Hasar": "Stok Fire ve Zararları",
    "Hırsızlık / Kayıp": "Stok Fire ve Zararları",
    "Sayım Eksiği": "Stok Fire ve Zararları",
    "Numune": "Pazarlama Giderleri",
    "Promosyon": "Pazarlama Giderleri",
    "Üretime Çıkış (Hammadde Sarfiyatı)": "Üretim Giderleri",
    "Tüketim (İç Kullanım)": "Genel Yönetim Giderleri"
};

frappe.ui.form.on('Stok Cikis Fisi', {
    onload: function (frm) {
        // Yeni kayıtsa ve firma/şube boşsa Personel'den çek
        if (frm.is_new()) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Personel",
                    filters: { kullanici: frappe.session.user },
                    fields: ["name", "firma", "sube"]
                },
                callback: function (r) {
                    if (r.message && r.message.length > 0) {
                        let personel = r.message[0];
                        if (!frm.doc.firma && personel.firma) {
                            frm.set_value('firma', personel.firma);
                        }
                        if (!frm.doc.sube && personel.sube) {
                            frm.set_value('sube', personel.sube);
                        }
                    }
                }
            });
        }
    },

    refresh: function (frm) {
        // Gider Hesabı Otomatik Seçilsin, Kullanıcı Ellemesin
        frm.set_df_property('gider_hesabi', 'read_only', 1);
    },

    cikis_tipi: function (frm) {
        if (frm.doc.cikis_tipi) {
            let hedef_hesap_adi = HESAP_ESLESMELERI[frm.doc.cikis_tipi];

            if (hedef_hesap_adi) {
                // Hesap Adından ID'yi bul
                frappe.db.get_value("Hesap", { hesap_adi: hedef_hesap_adi }, "name")
                    .then(r => {
                        if (r && r.message && r.message.name) {
                            frm.set_value("gider_hesabi", r.message.name);
                        } else {
                            frappe.msgprint(__("'{0}' adında bir hesap bulunamadı. Lütfen Hesap Planını kontrol edin.", [hedef_hesap_adi]));
                            frm.set_value("gider_hesabi", "");
                        }
                    });
            } else {
                // Eşleşme yoksa boşalt
                frm.set_value("gider_hesabi", "");
            }
        }
    }
});

frappe.ui.form.on('Stok Cikis Kalemi', {
    // Ürün seçildiğinde tetiklenir
    urun: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];

        // Kaynak depo seçilmemişse uyar
        if (!frm.doc.kaynak_depo) {
            frappe.msgprint(__("Lütfen önce Kaynak Depo seçiniz."));
            frappe.model.set_value(cdt, cdn, "urun", ""); // Ürünü temizle
            return;
        }

        if (row.urun) {
            frappe.db.get_value('Stok Bakiyesi',
                {
                    'urun': row.urun,
                    'depo': frm.doc.kaynak_depo
                },
                ['mevcut_miktar', 'birim_maliyet']
            ).then(r => {
                let current_qty = 0;
                let unit_cost = 0;

                if (r && r.message) {
                    current_qty = r.message.mevcut_miktar || 0;
                    unit_cost = r.message.birim_maliyet || 0;
                }

                // Satırdaki alanları doldur
                frappe.model.set_value(cdt, cdn, 'anlik_stok', current_qty);
                frappe.model.set_value(cdt, cdn, 'birim_maliyet', unit_cost);
            });
        }
    },

    // Miktar girildiğinde kontrol et
    cikis_miktari: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.cikis_miktari > row.anlik_stok) {
            frappe.msgprint({
                title: __('Yetersiz Stok'),
                message: __('Dikkat: Çıkış miktarı ({0}), anlık stoktan ({1}) fazla.', [row.cikis_miktari, row.anlik_stok]),
                indicator: 'orange'
            });
        }
    }
});
