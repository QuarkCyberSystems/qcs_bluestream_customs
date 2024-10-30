// Copyright (c) 2024, QCS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Estimation", {
	// refresh(frm) {

	// },
    // custom_turn_around_timetat_days: function(frm, cdt, cdn) {  
    //     let row = locals[cdt][cdn];
    //     let days_to_add = parseInt(row.custom_turn_around_timetat_days);
    //     let start_date = frm.doc.custom_date_of_enquiry;  
    //     console.log(start_date)
    //     if (days_to_add && start_date) {
    //         frappe.call({
    //             method: "qcs_bluestream_customs.qcs_bluestream_customs.doctype.estimation.estimation.calculate_turn_around_time_date",
    //             args: {
    //                 row_name: row.name,
    //                 days_to_add: days_to_add,
    //                 start_date: start_date  
    //             },
    //             callback: function(r) {
    //                 if (r.message) {
    //                     console.log(r.message)
    //                     frappe.model.set_value(cdt, cdn, 'custom_turn_around_time_date', r.message);
    //                     frm.refresh_field('budget_table');
    //                 }
    //             }
    //         });
    //     }
    // }
});
