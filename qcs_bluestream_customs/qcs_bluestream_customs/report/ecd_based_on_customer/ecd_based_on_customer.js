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
			"options": ["Quotation Pending", "Under Negotiation", "PO Confirmed", "Set as lost", "On track", "Delayed", "Prolonged Delay", "Order Closed", "Lost", "Cancelled"],
			"default": "Lost",
			"reqd": 1
		},

	]
};
