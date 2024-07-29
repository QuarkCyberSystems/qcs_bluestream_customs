// Copyright (c) 2024, QCS and contributors
// For license information, please see license.txt

frappe.query_reports["Purchase Tracker"] = {
	filters: [
		// {
		// 	fieldname: "company",
		// 	label: __("Company"),
		// 	fieldtype: "Link",
		// 	options: "Company",
		// 	default: frappe.defaults.get_user_default("Company"),
		// },
		// {
		// 	fieldname: "cost_center",
		// 	label: __("Cost Center"),
		// 	fieldtype: "Link",
		// 	options: "Cost Center",
		// },
		{
			fieldname: "purchase_order",
			label: __("Purchase Order"),
			fieldtype: "Link",
			options: "Purchase Order",
		},
		// {
        //     fieldname: "status",
        //     label: __("Status"),
        //     fieldtype: "Select",
        //     options: ["Draft"],
        //     default: "Draft"
        // }
		// {
		// 	fieldname: "from_date",
		// 	label: __("From Date"),
		// 	fieldtype: "Date",
		// 	default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[1],
		// },
		// {
		// 	fieldname: "to_date",
		// 	label: __("To Date"),
		// 	fieldtype: "Date",
		// 	default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[2],
		// },
	],
};
