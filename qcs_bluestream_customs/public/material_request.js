frappe.ui.form.on('Material Request', {
    refresh: (frm) => {
        if(cur_frm.doc.docstatus == 1  && frm.doc.status != 'Stopped'){
            frm.add_custom_button('Create Pick List', function() {
                frappe.model.open_mapped_doc({
                    method: "qcs_bluestream_customs.controller.material_request.create_pick_list",
                    frm: frm
                });
            }, __('Create'));
        }
    }
})