// Copyright (c) 2024, Quark Cyber Systems FZC
// For license information, please see license.txt


frappe.ui.form.on('Quality Inspection', {
    onload(frm) {
        frm.toggle_reqd([
            "reference_type",
            "reference_name",
        ], false);
    },
    inspection_type(frm) {
        if ( frm.doc.inspection_type == 'Incoming' ) {
            frm.toggle_reqd([
                "reference_type",
                "reference_name",
            ], true);     
        } else {
            frm.toggle_reqd([
                "reference_type",
                "reference_name",
            ], false);  
        }
    },
	validate(frm) {
		$.each(frm.doc.readings || [], function(i, d) {
			if(!d.manual_inspection) d.manual_inspection = frm.doc.manual_inspection;
		});
		refresh_field("readings");
	}
});
