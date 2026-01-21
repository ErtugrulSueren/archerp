import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, today

class SatinAlmaSiparisi(Document):
    def validate(self):
        if self.docstatus == 0:
            self.calculate_totals()

    def calculate_totals(self):
        total_net = 0.0
        total_tax = 0.0
        tax_inclusive = self.vergi_dahil_mi == 1
        
        for item in self.kalemler:
            qty = flt(item.miktar)
            price = flt(item.birim_fiyat)
            tax_rate = flt(item.vergi_orani)
            
            if tax_inclusive:
                net_unit_price = price / (1 + (tax_rate / 100.0))
                unit_tax = price - net_unit_price
            else:
                net_unit_price = price
                unit_tax = net_unit_price * (tax_rate / 100.0)
            
            line_net = qty * net_unit_price
            line_tax = qty * unit_tax
            
            item.tutar = line_net
            # Sipariş için birim maliyet saklamak isteyebiliriz ama fiyatta tutarlıysa gerek yok
            
            total_net += line_net
            total_tax += line_tax
            
        self.ara_toplam = total_net
        self.vergi_toplami = total_tax
        
        discount = flt(self.ek_iskonto_tutari)
        grand_total = total_net + total_tax - discount
        
        if grand_total < 0:
            grand_total = 0.0
            
        self.genel_toplam = grand_total

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
