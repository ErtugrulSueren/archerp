frappe.ui.form.on("Muhasebe Defteri", {
    refresh(frm) {
        // Muhatap Tipi alanını sadece ilgili doküman türleri gelecek şekilde filtrele
        frm.set_query("muhatap_tipi", function () {
            return {
                "filters": [
                    ["DocType", "name", "in", ["Tedarikci", "Musteri"]]
                ]
            };
        });
    },
});
