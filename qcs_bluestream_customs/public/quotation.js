frappe.ui.form.on('Quotation', {
    refresh: (frm) => {
        if(cur_frm.doc.docstatus ===0 && frm.doc.status == 'Draft') {
            frm.add_custom_button('Estimation', function() {
                frappe.model.open_mapped_doc({
                    method: "qcs_bluestream_customs.controller.quotation.create_estimation",
                    frm: frm
                });
            }, __('Create'));
        }
        if(cur_frm.doc.docstatus ===1) {
            frm.add_custom_button('Drawing Request', function() {
                frappe.model.open_mapped_doc({
                    method: "qcs_bluestream_customs.controller.quotation.create_drawing_request",
                    frm: frm
                });
            }, __('Create'));
            frm.add_custom_button('Design Request', function() {
                frappe.model.open_mapped_doc({
                    method: "qcs_bluestream_customs.controller.quotation.create_design_request",
                    frm: frm
                });
            }, __('Create'));
            frm.add_custom_button('Opportunity', function() {
                frappe.model.open_mapped_doc({
                    method: "qcs_bluestream_customs.controller.quotation.create_opportunity",
                    frm: frm
                });
            }, __('Create'));
        }
        
    }
});
