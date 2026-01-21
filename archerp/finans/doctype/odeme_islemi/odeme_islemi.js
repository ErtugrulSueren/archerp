// Copyright (c) 2025, Ertu and contributors
// For license information, please see license.txt

frappe.ui.form.on('Odeme Islemi', {
    refresh: function (frm) {
        // Referans Tipi alanını sadece Satış Faturası ve Satın Alma Faturası ile kısıtla
        frm.set_query('referans_tipi', function () {
            return {
                filters: {
                    name: ['in', ['Satis Faturasi', 'Satin Alma Faturasi']]
                }
            };
        });

        // Ödeme Yöntemine göre Kasa/Banka filtresi
        frm.set_query('kasa_banka', function () {
            let account_type = [];
            if (frm.doc.odeme_yontemi === 'Nakit') {
                account_type = ['Nakit (Cash)'];
            } else if (['Havale/EFT', 'Kredi Kartı', 'Çek/Senet'].includes(frm.doc.odeme_yontemi)) {
                account_type = ['Banka (Bank)'];
            }

            if (account_type.length > 0) {
                return {
                    filters: {
                        account_type: ['in', account_type]
                    }
                };
            }
        });

        // Eğer referans tipi boşsa, ödeme türüne göre ayarla
        if (!frm.doc.referans_tipi && frm.doc.odeme_turu) {
            frm.trigger('odeme_turu');
        }

        // Taraf Kişi seçili ama Hesap boşsa (Ödeme Al butonu ile gelindiyse)
        if (frm.doc.taraf_tipi && frm.doc.taraf_kisi && !frm.doc.taraf_hesabi) {
            frm.trigger('taraf_kisi');
        }
    },

    odeme_yontemi: function (frm) {
        // Yöntem değişince tetikle ki query güncellensin.
        // Gerekirse mevcut seçimi temizle eğer tipe uymuyorsa (isteğe bağlı, şimdilik sadece filtre güncelleyelim)
        frm.set_value('kasa_banka', null);
    },

    odeme_turu: function (frm) {
        if (frm.doc.odeme_turu === 'Tahsilat(Al)') {
            frm.set_value('referans_tipi', 'Satis Faturasi');
            frm.set_value('taraf_tipi', 'Musteri');
        } else if (frm.doc.odeme_turu === 'Tediye(Ver)') {
            frm.set_value('referans_tipi', 'Satin Alma Faturasi');
            frm.set_value('taraf_tipi', 'Tedarikci');
        }
    },

    taraf_kisi: function (frm) {
        if (frm.doc.taraf_tipi && frm.doc.taraf_kisi) {
            frappe.db.get_value(frm.doc.taraf_tipi, frm.doc.taraf_kisi, 'muhasebe_hesabi')
                .then(r => {
                    if (r && r.message && r.message.muhasebe_hesabi) {
                        frm.set_value('taraf_hesabi', r.message.muhasebe_hesabi);
                    }
                });
        }
    }
});


