import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, today
from archerp.controllers.transaction_controller import TransactionController

class SatinAlmaSiparisi(TransactionController):
    def validate(self):
        if self.docstatus == 0:
            self.calculate_totals()

    def on_submit(self):
        self.guncelle_durum()
        self.teklif_durum_guncelle("Siparis Verildi")

    def on_cancel(self):
        self.guncelle_durum()
        self.teklif_durum_guncelle("Kabul Edildi")

    def teklif_durum_guncelle(self, durum):
        if self.teklif_referansi:
            frappe.db.set_value("Satin Alma Teklifi", self.teklif_referansi, "status", durum)

    def guncelle_durum(self):
        if self.docstatus != 1:
            return

        toplam_miktar = 0
        toplam_teslim = 0
        toplam_fatura = 0

        for item in self.kalemler:
            toplam_miktar += flt(item.miktar)
            toplam_teslim += flt(item.teslim_alinan_miktar)
            toplam_fatura += flt(item.faturalanan_miktar)

        status = "Teslim Alınacak" 
        
        # Mantık Önceliği
        if toplam_teslim >= toplam_miktar and toplam_fatura >= toplam_miktar:
            status = "Tamamlandı"
        elif toplam_teslim >= toplam_miktar:
            status = "Faturalanacak"
        elif toplam_fatura > 0:
            status = "Kısmi Faturalandı"
        elif toplam_teslim > 0:
             status = "Kısmi Teslim Alındı"
        else:
             status = "Teslim Alınacak"
             
        self.db_set('status', status)

    def guncelle_teslim_alinan(self):
        for item in self.kalemler:
            item.teslim_alinan_miktar = 0.0
            
        mal_kabul_kalemleri = frappe.db.sql("""
            SELECT mkk.siparis_kalemi_id, SUM(mkk.miktar) as kabul_miktar
            FROM `tabMal Kabul Kalemi` mkk
            JOIN `tabMal Kabul Fisi` mkf ON mkk.parent = mkf.name
            WHERE mkf.docstatus = 1 AND mkk.siparis_kalemi_id IN (
                SELECT name FROM `tabSatin Alma Kalemi` WHERE parent = %s
            )
            GROUP BY mkk.siparis_kalemi_id
        """, (self.name), as_dict=True)
        
        for row in mal_kabul_kalemleri:
            for item in self.kalemler:
                if item.name == row.siparis_kalemi_id:
                    item.teslim_alinan_miktar = flt(row.kabul_miktar)
                    
        self.save(ignore_permissions=True)
        self.guncelle_durum()

    def guncelle_faturalanan(self):
        for item in self.kalemler:
            item.faturalanan_miktar = 0.0
            
        fatura_kalemleri = frappe.db.sql("""
            SELECT safk.siparis_kalemi_id, SUM(safk.miktar) as fatura_miktar
            FROM `tabSatin Alma Fatura Kalemi` safk
            JOIN `tabSatin Alma Faturasi` saf ON safk.parent = saf.name
            WHERE saf.docstatus = 1 AND safk.siparis_kalemi_id IN (
                SELECT name FROM `tabSatin Alma Kalemi` WHERE parent = %s
            )
            GROUP BY safk.siparis_kalemi_id
        """, (self.name), as_dict=True)
        
        for row in fatura_kalemleri:
            for item in self.kalemler:
                if item.name == row.siparis_kalemi_id:
                    item.faturalanan_miktar = flt(row.fatura_miktar)
        
        self.save(ignore_permissions=True)
        self.guncelle_durum()

@frappe.whitelist()
def make_mal_kabul_fisi(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.tarih = today()
        target.satin_alma_siparisi_referansi = source.name # Referans
        
        items_to_remove = []
        for item in target.kalemler:
             source_item_id = item.siparis_kalemi_id
             if source_item_id:
                  source_item = next((i for i in source.kalemler if i.name == source_item_id), None)
                  if source_item:
                       remaining_qty = flt(source_item.miktar) - flt(source_item.teslim_alinan_miktar)
                       if remaining_qty <= 0:
                            items_to_remove.append(item)
                       else:
                            item.miktar = remaining_qty
        
        for item in items_to_remove:
             target.kalemler.remove(item)
             
        if not target.kalemler:
             frappe.throw("Bu siparişin tüm ürünleri zaten teslim alınmış!")

    doclist = get_mapped_doc("Satin Alma Siparisi", source_name, {
        "Satin Alma Siparisi": {
            "doctype": "Mal Kabul Fisi",
            "field_map": {
                "name": "satin_alma_siparisi_referansi", # Alternatif map
                "tedarikci": "tedarikci",
                "tedarikci_adi": "tedarikci_adi",
                "sube": "sube",
                "para_birimi": "para_birimi",
                "doviz_kuru": "doviz_kuru",
                "hedef_depo": "hedef_depo",
                "odeme_kosulu": "odeme_kosulu",
                "sartlar_ve_kosullar": "sartlar_ve_kosullar",
                "vergi_dahil_mi": "vergi_dahil_mi"
            }
        },
        "Satin Alma Kalemi": {
            "doctype": "Mal Kabul Kalemi",
            "field_map": {
                "name": "siparis_kalemi_id",
                "urun": "urun",
                "urun_adi": "urun_adi",
                "miktar": "miktar",
                "birim_maliyet": "birim_maliyet",
                "birim_fiyat": "birim_fiyat", # Eğer mal kabulde fiyat varsa
                "stok_birimi": "stok_birimi",
                "depo": "depo",
                "vergi_sablonu": "vergi_sablonu",
                "vergi_orani": "vergi_orani"
            }
        }
    }, target_doc, set_missing_values)

    return doclist
