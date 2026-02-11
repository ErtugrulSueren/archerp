import frappe
from frappe.utils import flt

def create_gl_entry(doc, account, debit, credit, cancel, party_type=None, party=None, remark=None):
    """
    Creates a General Ledger (GL) Entry.
    
    Args:
        doc (Document): The document creating the entry (self).
        account (str): Account Name or ID.
        debit (float): Debit amount.
        credit (float): Credit amount.
        cancel (bool): If True, reverses the entry (Debit <-> Credit).
        party_type (str, optional): 'Musteri', 'Tedarikci', etc.
        party (str, optional): Party name.
        remark (str, optional): Description. Defaults to "{DocType}: {Name}".
    """
    
    if debit == 0 and credit == 0:
            return
            
    # Apply Exchange Rate
    # Fetch from doc if available
    exchange_rate = flt(getattr(doc, "doviz_kuru", 1))
    if exchange_rate <= 0: exchange_rate = 1.0
    
    debit = debit * exchange_rate
    credit = credit * exchange_rate
            
    gl = frappe.new_doc("Muhasebe Defteri")

    gl.belge_tipi = doc.doctype
    gl.belge_no = doc.name
    gl.tarih = doc.tarih
    gl.hesap = account
    gl.aciklama = remark or f"{doc.doctype}: {doc.name}"
    gl.muhatap_tipi = party_type
    gl.carimuhatap = party
    
    # Firma ve Şube bilgilerini kaynak belgeden aktar
    if hasattr(doc, "firma") and doc.firma:
        gl.firma = doc.firma
    if hasattr(doc, "sube") and doc.sube:
        gl.sube = doc.sube
    
    if cancel:
            # Reverse for cancellation
            gl.borc = credit
            gl.alacak = debit
    else:
            gl.borc = debit
            gl.alacak = credit
            
    gl.insert(ignore_permissions=True)
