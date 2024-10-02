frappe.ui.form.on('Opportunity', {
    refresh: function (frm) {
        var doc = frm.doc;
        if(!frm.is_new() && doc.status !== "Lost") {
            frm.add_custom_button('Estimation', function() {
                frappe.model.open_mapped_doc({
                    method: "qcs_bluestream_customs.controller.opportunity.create_estimation",
                    frm: frm
                });
            }, __('Create'));
           
        }
        
    }
});
