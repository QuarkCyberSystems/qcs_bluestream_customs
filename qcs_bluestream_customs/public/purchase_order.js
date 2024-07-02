frappe.ui.form.on('Purchase Order', {
    refresh: (frm) => {
        if(cur_frm.doc.docstatus ===1 && frm.doc.status !== 'Closed' && frm.doc.status !== 'On Hold') {
            frm.add_custom_button('Shipping Tracker', function() {
                frappe.model.open_mapped_doc({
                    method: "qcs_bluestream_customs.controller.purchase_order.create_shipping_tracker",
                    frm: frm
                });
            }, __('Create'));
        }
        
    }
})