
import frappe
from frappe.model.document import Document

class Urun(Document):
    def validate(self):
        """
        Ürün validasyonları:
        1. Hem Şablon (has_variants) hem Varyant (varyant_mi) olamaz.
        2. Varyant ise, Varyantı Olduğu Ürün (varyanti_oldugu_urun) zorunludur.
        """
        
        # Boolean check helper
        is_template = self.has_variants == 1 or self.has_variants == "1"
        is_variant = self.varyant_mi == 1 or self.varyant_mi == "1"

        # Kural 1: Çelişki Kontrolü
        if is_template and is_variant:
            frappe.throw(
                title="Hatalı Yapılandırma",
                msg="Bir ürün aynı anda hem <b>Varyant Şablonu</b> hem de <b>Varyant</b> olamaz.<br>Lütfen sadece birini seçiniz.",
                exc=frappe.ValidationError
            )
            
        # Kural 2: Parent Zorunluluğu
        if is_variant and not self.varyanti_oldugu_urun:
            frappe.throw(
                title="Eksik Bilgi",
                msg="Bu ürünü <b>Varyant</b> olarak işaretlediniz. Lütfen <b>Varyantı Olduğu Ürün</b> alanını doldurunuz.",
                exc=frappe.ValidationError
            )

    def on_update(self):
        """
        Varyant Yönetimi (Sadece Şablon Ürünler İçin):
        Aşama A: Eksik varyantları oluştur (Tablolar dahil).
        Aşama B: Mevcut varyantları tam senkronize et (Tablolar dahil).
        """
        if self.has_variants == 1 or self.has_variants == "1":
            self.create_missing_variants()
            self.sync_existing_variants()

    def on_trash(self):
        """
        Silme İşlemi:
        Eğer bu bir şablon ürünse, buna bağlı tüm varyantları da otomatik sil.
        Böylece Link hatası (417) almadan silme işlemi gerçekleşebilir.
        """
        if self.has_variants == 1 or self.has_variants == "1":
            variants = frappe.get_all("Urun", filters={"varyanti_oldugu_urun": self.name})
            if variants:
                for v in variants:
                    try:
                        frappe.delete_doc("Urun", v.name, ignore_permissions=True, force=1)
                    except Exception as e:
                        # Eğer zaten silinmişse veya başka bir sorun varsa logla ama süreci durdurma
                        print(f"Varyant silinemedi: {v.name}. Hata: {e}")

    def create_missing_variants(self):
        """
        Tablodaki özellikler için kombinasyonel (Cartesian) varyantları oluşturur.
        Örn: Renk: Kırmızı, Mavi | Beden: S, M
        Sonuç: Kırmızı-S, Kırmızı-M, Mavi-S, Mavi-M
        """
        if not self.varyant_ozellikleri:
            return

        import itertools

        # 1. Özellikleri Grupla (Kartesyan Hazırlığı)
        # attrs = { "Renk": ["Kırmızı", "Mavi"], "Beden": ["S", "M"] }
        attrs = {}
        for row in self.varyant_ozellikleri:
            if not row.ozellik or not row.ozellik_degeri:
                continue
            
            # Başlıkları temizle (Link field olduğu için row.ozellik key olarak kullanılır)
            key = row.ozellik.strip()
            
            # Değerleri ayıkla (Virgülle ayrılmış)
            values = [x.strip() for x in row.ozellik_degeri.split(',') if x.strip()]
            
            if key in attrs:
                # Aynı özellikten birden fazla satır varsa birleştir (Örn: 2 tane Renk satırı)
                attrs[key].extend(values)
            else:
                attrs[key] = values

        # Tekrar eden değerleri temizle (Örn: İki satırda da 'Kırmızı' varsa)
        for k in attrs:
            attrs[k] = list(set(attrs[k]))

        if not attrs:
            return

        # 2. Kombinasyonları Oluştur
        # keys = ["Renk", "Beden"]
        # lists = [ ["Kırmızı", "Mavi"], ["S", "M"] ]
        keys = list(attrs.keys())
        value_lists = [attrs[k] for k in keys]
        
        combinations = list(itertools.product(*value_lists))

        for combo in combinations:
            # combo = ("Kırmızı", "S") vb.
            
            # Suffix Oluştur: KIRMIZI-S
            suffix_parts = [str(x).upper().replace(" ", "-") for x in combo]
            suffix = "-".join(suffix_parts)
            
            new_item_code = f"{self.urun_kodu}-{suffix}"
            
            # İsim Oluştur: Ürün Adı - Kırmızı/S
            name_suffix = "/".join(combo)
            new_item_name = f"{self.urun_adi} - {name_suffix}"

            if not frappe.db.exists("Urun", new_item_code):
                # Yeni Varyant
                new_variant = frappe.new_doc("Urun")
                new_variant.urun_kodu = new_item_code
                new_variant.urun_adi = new_item_name
                
                # İlişkiler
                new_variant.varyant_mi = 1
                new_variant.has_variants = 0
                new_variant.varyanti_oldugu_urun = self.name
                
                # Varyant Özelliklerini Metin Olarak Kaydet (Bilgi amaçlı)
                # "Renk: Kırmızı, Beden: S"
                desc_parts = []
                for i, val in enumerate(combo):
                    desc_parts.append(f"{keys[i]}: {val}")
                new_variant.varyant_aciklamasi = ", ".join(desc_parts)

                # Alanları ve Tabloları Kopyala
                self.copy_attributes(new_variant)
                
                # Kaydet
                new_variant.insert(ignore_permissions=True)
                frappe.msgprint(f"Otomatik Varyant Oluşturuldu: {new_variant.name}")

    def sync_existing_variants(self):
        """
        Mevcut varyantları yükler ve tablolar dahil günceller.
        """
        variants = frappe.get_all("Urun", filters={"varyanti_oldugu_urun": self.name})
        
        if not variants:
            return

        count = 0
        for v in variants:
            # Varyantı tam yükle (Tablolarla birlikte)
            variant_doc = frappe.get_doc("Urun", v.name)
            
            # Alanları ve Tabloları Eşitle
            self.copy_attributes(variant_doc)
            
            # Kaydet (Validasyonlar ve hooklar çalışsın)
            variant_doc.save(ignore_permissions=True)
            count += 1
        
        if count > 0:
            frappe.msgprint(f"{count} adet varyantın tüm bilgileri (tablolar dahil) güncellendi.")

    def copy_attributes(self, target_doc):
        """
        Hedef dokümana ana ürünün özelliklerini ve tablolarını kopyalar.
        Fiyat, Stok, Barkod HARİÇ.
        """
        # 1. Basit Alanlar
        target_doc.urun_grubu = self.urun_grubu
        target_doc.stok_birimi = self.stok_birimi
        target_doc.marka = self.marka
        target_doc.model = self.model
        target_doc.vergi_sablonu = self.vergi_sablonu
        target_doc.raf_omru_gun = self.raf_omru_gun
        target_doc.garanti_ay = self.garanti_ay
        target_doc.varsayilan_depo = self.varsayilan_depo
        target_doc.detayli_aciklama = self.detayli_aciklama
        # Fiyatlar
        target_doc.standart_satis_fiyati = self.standart_satis_fiyati
        target_doc.standart_alis_fiyati = self.standart_alis_fiyati
        target_doc.gider_hesabi = self.gider_hesabi
        
        # Yeni eklenen alanlar
        target_doc.seri_numarasi_var_mi = self.seri_numarasi_var_mi
        target_doc.parti_takibi = self.parti_takibi

        # 2. Tablo: Birim Çevrimleri
        # Mevcut satırları temizle
        target_doc.set("birim_cevrimleri", [])
        # Ana üründen yenileri ekle
        for row in self.get("birim_cevrimleri", []):
            target_doc.append("birim_cevrimleri", {
                "birim": row.birim,
                "cevrim_katsayisi": row.cevrim_katsayisi
            })

        # 3. Tablo: Tedarikçi Bilgileri
        target_doc.set("tedarikci_bilgileri", [])
        for row in self.get("tedarikci_bilgileri", []):
            target_doc.append("tedarikci_bilgileri", {
                "tedarikci": row.tedarikci,
                "tedarikci_urun_kodu": row.tedarikci_urun_kodu,
                "is_default": row.is_default
            })
