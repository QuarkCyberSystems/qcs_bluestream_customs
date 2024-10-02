// Copyright (c) 2024, QCS and contributors
// For license information, please see license.txt

frappe.query_reports["Turn Around Time Report"] = {
	"filters": [
		{
			fieldname: "estimation_no",
			label: __("Estimation"),
			fieldtype: "Link",
			options: "Estimation",
		},
		{
			fieldname: "quotation_no",
			label: __("Quotation"),
			fieldtype: "Link",
			options: "Quotation",
		},
		{
			fieldname: "docstatus",
			label: __("Status"),
			fieldtype: "Select",
			options: [
				{ "label": __("Draft"), "value": "0" },
				{ "label": __("Submitted"), "value": "1" }
			],
			default: "0"
		}
	]
};
