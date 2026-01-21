import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import today

from frappe.utils import flt

class SatinAlmaTeklifi(Document):
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
        self.db_set("status", "Kabul Edildi")

@frappe.whitelist()
def make_satin_alma_siparisi(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.tarih = today()
        target.beklenen_teslim = today() # Varsayılan bugün, kullanıcı değiştirebilir
        
        # Gider Hesaplarını ve Vergi Şablonlarını Doldur
        # target.kalemler ve source.kalemler sıralı olduğu varsayılır (get_mapped_doc standardı)
        # target.kalemler ve source.kalemler sıralı olduğu varsayılır (get_mapped_doc standardı)
        for target_item, source_item in zip(target.kalemler, source.kalemler):
             # 1. Kaynaktan (Tekliften) Al (Eğer maplenmediyse)
             if not target_item.vergi_sablonu and source_item.vergi_sablonu:
                  target_item.vergi_sablonu = source_item.vergi_sablonu
             
             if not target_item.vergi_orani and source_item.vergi_orani:
                  target_item.vergi_orani = source_item.vergi_orani

             # 2. Ürün Kartından Al (Eğer hala boşsa)
             if target_item.urun:
                  fields_to_fetch = []
                  if not target_item.gider_hesabi: fields_to_fetch.append("gider_hesabi")
                  if not target_item.vergi_sablonu: fields_to_fetch.append("vergi_sablonu")
                  
                  if fields_to_fetch:
                       product_data = frappe.db.get_value("Urun", target_item.urun, fields_to_fetch, as_dict=True)
                       if product_data:
                            if "gider_hesabi" in product_data and product_data.gider_hesabi and not target_item.gider_hesabi:
                                 target_item.gider_hesabi = product_data.gider_hesabi
                            if "vergi_sablonu" in product_data and product_data.vergi_sablonu and not target_item.vergi_sablonu:
                                 target_item.vergi_sablonu = product_data.vergi_sablonu
        
    doclist = get_mapped_doc("Satin Alma Teklifi", source_name, {
        "Satin Alma Teklifi": {
            "doctype": "Satin Alma Siparisi",
            "field_map": {
                "name": "teklif_referansi", # Siparişte bu alan var mı kontrol etmeli, yoksa notlara eklenebilir veya özel alan açılabilir. Ancak standart map yapıyoruz.
                "tedarikci": "tedarikci",
                "sube": "sube",
                "para_birimi": "para_birimi",
                "doviz_kuru": "doviz_kuru",
                "vergi_dahil_mi": "vergi_dahil_mi",
                "odeme_kosulu": "odeme_kosulu",
                "sartlar_ve_kosullar": "sartlar_ve_kosullar",
                "hedef_depo": "hedef_depo",
                "ek_iskonto_tutari": "ek_iskonto_tutari",
                "notlar": "notlar"
            }
        },
        "Satin Alma Teklif Kalemi": {
            "doctype": "Satin Alma Kalemi",
            "field_map": {
                "urun": "urun",
                "urun_adi": "urun_adi",
                "miktar": "miktar",
                "birim_fiyat": "birim_fiyat",
                "stok_birimi": "stok_birimi",
                "vergi_sablonu": "vergi_sablonu",
                "vergi_orani": "vergi_orani"
            }
        }
    }, target_doc, set_missing_values)

    return doclist
