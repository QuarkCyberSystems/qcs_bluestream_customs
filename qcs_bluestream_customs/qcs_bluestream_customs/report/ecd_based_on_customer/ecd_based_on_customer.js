// Copyright (c) 2024, QCS and contributors
// For license information, please see license.txt

frappe.query_reports["ECD Based on Customer"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname":"status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": ["", "Quotation Pending", "Under Negotiation", "PO Confirmed", "Set as lost", "On track", "Delayed", "Prolonged Delay", "Order Closed", "Lost", "Cancelled"],
		},
		{
			"fieldname":"quotation_to",
			"label": __("Quotation To"),
			"fieldtype": "Select",
			"options": ["", "Customer", "Lead"]
		},
		{
			"fieldname":"jih__tender",
			"label": __("JIH / Tender "),
			"fieldtype": "Select",
			"options": ["", "JIH", "Tender"],
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"depends_on": "eval:doc.quotation_to=='Customer'",
		},
		{
			"fieldname":"lead",
			"label": __("Lead"),
			"fieldtype": "Link",
			"options": "Lead",
			"depends_on": "eval:doc.quotation_to=='Lead'",
		},
		{
			"fieldname":"employee",
			"label": __("Sales Person"),
			"fieldtype": "Link",
			"options": "Employee"
		},
		
	],
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (data && (data.status)) {
			value = `<span style="font-weight: bold;">${value}</span>`;
		}
		return value;
	},
};
