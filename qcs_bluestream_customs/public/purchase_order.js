frappe.ui.form.on('Purchase Order', {
    refresh: (frm) => {
        if(cur_frm.doc.docstatus ===1 && frm.doc.status !== 'Closed' && frm.doc.status !== 'On Hold') {
            frm.add_custom_button('Shipping Tracker', function() {
                
            }, __('Create'));
        }
    }
})