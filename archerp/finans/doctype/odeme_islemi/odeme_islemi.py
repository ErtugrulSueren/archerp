
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class OdemeIslemi(Document):
    def validate(self):
        """Hata Önleme ve Toplam Kontrolü"""
        # "Odenen Tutar" validasyonu
        if self.odenen_tutar <= 0:
            frappe.throw("Ödenen Tutar 0'dan büyük olmalıdır.")

    def on_submit(self):
        # 1. Muhasebe Kaydı
        self.muhasebe_islemi_yap(iptal_mi=False)
        
        # 2. Faturaları Güncelle (Single Doc Link)
        self.faturayi_guncelle(islem_yonu=1)

    def on_cancel(self):
        # 1. Muhasebe Ters Kayıt
        self.muhasebe_islemi_yap(iptal_mi=True)
        
        # 2. Faturaları Geri Al (Single Doc Link)
        self.faturayi_guncelle(islem_yonu=-1)

    def muhasebe_islemi_yap(self, iptal_mi=False):
        """Tahsilat veya Tediye durumuna göre GL Entry oluşturur"""
        
        # Taraf Kişi (ID) ve Name kullanarak açıklama
        aciklama = f"{self.odeme_turu}: {self.taraf_kisi} - {self.name}"
        if iptal_mi: aciklama = f"İPTAL: {aciklama}"

        # Yön Belirleme
        # Tahsilat(Al): Kasa (Borç), Taraf (Alacak)
        # Tediye(Ver):  Taraf (Borç), Kasa (Alacak)
        
        is_tahsilat = (self.odeme_turu == "Tahsilat(Al)")
        
        # Ana Tutar
        tutar = self.odenen_tutar
        
        # KASA / BANKA HESABI İŞLEMİ
        # ---------------------------
        kasa_borc = 0
        kasa_alacak = 0
        
        if is_tahsilat:
            kasa_borc = tutar # Para Giriyor
        else:
            kasa_alacak = tutar # Para Çıkıyor

        # İptal durumunda tam tersi
        if iptal_mi:
            kasa_borc, kasa_alacak = kasa_alacak, kasa_borc

        self.gl_kayit(self.kasa_banka, kasa_borc, kasa_alacak, aciklama)

        # TARAF (CARİ) HESABI İŞLEMİ
        # --------------------------
        cari_borc = 0
        cari_alacak = 0
        
        if is_tahsilat:
            cari_alacak = tutar # Müşteri borcu düşüyor (Alacak)
        else:
            cari_borc = tutar # Tedarikçi borcu düşüyor (Borç)

        # İptal durumunda tam tersi
        if iptal_mi:
            cari_borc, cari_alacak = cari_alacak, cari_borc

        self.gl_kayit(self.taraf_hesabi, cari_borc, cari_alacak, aciklama)

    def gl_kayit(self, hesap, borc, alacak, aciklama):
        gl = frappe.new_doc("Muhasebe Defteri")
        gl.tarih = self.tarih
        gl.hesap = hesap
        gl.borc = flt(borc)
        gl.alacak = flt(alacak)
        gl.belge_tipi = "Odeme Islemi"
        gl.belge_no = self.name
        gl.aciklama = aciklama
        
        # Dinamik Muhatap (Müşteri veya Tedarikçi)
        # Taraf Tipi (DocType) ve Taraf Kişi (ID) alanlarını kullanıyoruz
        gl.muhatap_tipi = self.taraf_tipi # Örn: 'Musteri'
        gl.carimuhatap = self.taraf_kisi  # Örn: 'MUS-001'
        
        gl.insert(ignore_permissions=True)

    def faturayi_guncelle(self, islem_yonu=1):
        """
        referans_tipi ve referans_no alanlarını kullanarak TEK BİR faturayı günceller.
        """
        if self.referans_tipi and self.referans_no and self.odenen_tutar > 0:
            
            if not frappe.db.exists(self.referans_tipi, self.referans_no):
                return
                
            doc = frappe.get_doc(self.referans_tipi, self.referans_no)
            
            # Değişimi hesapla
            degisim = flt(self.odenen_tutar) * islem_yonu
            
            # Faturadaki odenen_tutar alanını güncelle
            mevcut_odenen = flt(doc.odenen_tutar) if hasattr(doc, 'odenen_tutar') else 0
            yeni_odenen = mevcut_odenen + degisim
            
            # Negatif olmasını engelle (Güvenlik)
            if yeni_odenen < 0: yeni_odenen = 0
            
            # db_set kullanarak güncelle
            if hasattr(doc, 'odenen_tutar'):
                doc.db_set('odenen_tutar', yeni_odenen)
            
            # DURUM GÜNCELLEME (STATUS)
            if hasattr(doc, 'status'):
                genel_toplam = flt(doc.genel_toplam)
                kalan = genel_toplam - yeni_odenen
                
                yeni_durum = doc.status 
                
                if yeni_odenen <= 0:
                    yeni_durum = "Ödenmedi"
                elif kalan <= 0.1: 
                    yeni_durum = "Ödendi"
                else:
                    yeni_durum = "Kısmi Ödendi"
                
                if doc.status != yeni_durum:
                    doc.db_set('status', yeni_durum)
