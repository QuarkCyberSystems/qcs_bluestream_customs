frappe.listview_settings["Job Card"] = {
    has_indicator_for_draft: true,
    add_fields: ["expected_start_date", "expected_end_date"],
    get_indicator: function (doc) {
        const status_colors = {
            "Work In Progress": "orange",
            Completed: "green",
            Cancelled: "red",
            "Material Transferred": "blue",
            Open: "red",
        };
        const status = doc.status || "Open";
        const color = status_colors[status] || "blue";

        return [__(status), color, `status,=,${status}`];
    },
    onload: function (listview) {
        listview.page.add_action_item(__("Pause"), () => {
            const selected = listview.get_checked_items();
            if (selected.length > 0) {
                const non_submitted = selected.filter((job_card) => job_card.docstatus === 0); 
                if (non_submitted.length > 0) {
                    non_submitted.forEach((job_card) => {
                        frappe.call({
                            method: "qcs_bluestream_customs.controller.job_card_automation.pause_job_card",
                            args: {
                                job_card_name: job_card.name,
                            },
                            callback: function (r) {
                                listview.refresh();
                                listview.clear_checked_items();
                                if (frappe.get_route()[0] === "Form" && frappe.get_route()[1] === "Job Card" && frappe.get_route()[2] === job_card.name) {
                                    // frappe.msgprint(`Pausing Job Card: ${job_card.name}`);
                                    setTimeout(() => {
                                        cur_frm.reload_doc();
                                    }, 500); 
                                }
                            },
                        });
                    });
                } else {
                    frappe.msgprint(__("No non-submitted Job Cards selected to pause."));
                }
            } else {
                frappe.msgprint(__("Please select at least one Job Card to pause."));
            }
        });

        // Resume action
        listview.page.add_action_item(__("Resume"), () => {
            const selected = listview.get_checked_items();
            if (selected.length > 0) {
                const non_submitted = selected.filter((job_card) => job_card.docstatus === 0); 
                if (non_submitted.length > 0) {
                    non_submitted.forEach((job_card) => {
                        frappe.call({
                            method: "qcs_bluestream_customs.controller.job_card_automation.resume_job_card",
                            args: {
                                job_card_name: job_card.name,
                            },
                            callback: function (r) {
                                listview.refresh();
                                listview.clear_checked_items();
                                if (frappe.get_route()[0] === "Form" && frappe.get_route()[1] === "Job Card" && frappe.get_route()[2] === job_card.name) {
                                    // frappe.msgprint(`Resuming Job Card: ${job_card.name}`);
                                    setTimeout(() => {
                                        cur_frm.reload_doc();
                                    }, 500);
                                }
                            },
                        });
                    });
                } else {
                    frappe.msgprint(__("No non-submitted Job Cards selected to resume."));
                }
            } else {
                frappe.msgprint(__("Please select at least one Job Card to resume."));
            }
        });
        listview.page.add_action_item(__("Skip Automation"), () => {
            const selected = listview.get_checked_items();
        
            if (selected.length > 0) {
                const non_submitted = selected.filter((job_card) => job_card.docstatus === 0);
                
                if (non_submitted.length > 0) {
                    non_submitted.forEach((job_card) => {
                        frappe.call({
                            method: "qcs_bluestream_customs.controller.job_card_automation.set_skip_automation",
                            args: {
                                job_card_name: job_card.name,
                            },
                            callback: function (r) {
                                listview.refresh();
                                listview.clear_checked_items();
                            },
                        });
                    });
                } else {
                    frappe.msgprint(__("No non-submitted Job Cards selected to skip automation."));
                }
            } else {
                frappe.msgprint(__("Please select at least one Job Card."));
            }
        });
        
    },
};
