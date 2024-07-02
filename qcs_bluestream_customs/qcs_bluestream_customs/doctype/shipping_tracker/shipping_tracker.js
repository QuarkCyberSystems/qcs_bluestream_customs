// Copyright (c) 2024, QCS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Shipping Tracker", {
	// refresh(frm) {

	// },
    onload:function(frm) {
		frappe.db.get_value("Supplier",{'name':frm.doc.supplier},'country').then(r => {
            if (r.message) {
                let country = r.message.country;
                frm.set_value("supplier_country",country)

            } 
        });

	}
});
