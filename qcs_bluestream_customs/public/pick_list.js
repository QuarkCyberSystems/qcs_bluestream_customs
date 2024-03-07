frappe.ui.form.on('Pick List', {
    refresh: (frm) => {
        if(cur_frm.doc.docstatus == 1){
            frm.add_custom_button('Create Stock Entry', function() {
                frappe.xcall('qcs_bluestream_customs.override.pick_list.create_stock_entry', {
                    'pick_list': frm.doc,
                }).then(stock_entry => {
                    frappe.model.sync(stock_entry);
                    frappe.set_route("Form", 'Stock Entry', stock_entry.name);
                });
            }, __('Create'));
        }
    }
})