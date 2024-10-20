// Copyright (c) 2024, QCS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Shipping Tracker", {
	refresh : (frm) => {
        if(cur_frm.doc.docstatus ===0) {
            frm.add_custom_button('Purchase Order', function() {
                let d = erpnext.utils.map_current_doc({
                    method: "qcs_bluestream_customs.controller.purchase_order.create_shipping_tracker",
                    source_doctype: "Purchase Order",
                    target: frm,
                    setters: [
                        {
                            label: "Supplier",
                            fieldname: "supplier",
                            fieldtype: "Link",
                            options: "Supplier",
                            default: frm.doc.supplier || undefined,
                        },
                    ],
                    get_query_filters: {
                        company: frm.doc.company,
                        docstatus: 1                    },
                });
                
            }, __('Get items From'));

        }

	},
    onload:function(frm) {
		frappe.db.get_value("Supplier",{'name':frm.doc.supplier},'country').then(r => {
            if (r.message) {
                let country = r.message.country;
                frm.set_value("supplier_country",country)

            } 
        });

	}
});
