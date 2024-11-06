import frappe
from frappe.model.mapper import get_mapped_doc


@frappe.whitelist()
def create_estimation(source_name, target_doc=None):
	doc = get_mapped_doc(
		"Quotation",
		source_name,
		{
			"Quotation": {
				"doctype": "Estimation",
				"field_map": {"name" :"quotation",
					"employee": "sales_person_employee",
					"employee_name": "employee_name",
                    "transaction_date": "quotation_date",
                    "custom_sales_person": "sales_person_custom",
                    "scope_of_work": "scope_of_work_1",
                    "contractor" :"contractor",
                    "priority" :"priority",
                    "client" :"client",
                    "rfq_no_project_name" :"project",
                    "custom_date_of_enquiry" :"date_of_enquiry",
                    "jih__tender" :"status"                    
                  
                },
				# "validation": {"docstatus": ["=", 1]},
			},
			
		},
		target_doc,
	)

	return doc


@frappe.whitelist()
def create_drawing_request(source_name, target_doc=None):
	doc = get_mapped_doc(
		"Quotation",
		source_name,
		{
			"Quotation": {
				"doctype": "Drawing Request",
				"field_map": {"name" :"quotation",
                    "contractor" :"contractor_name",
                    "consultant" :"contractor_name",
                    "customer_name" :"customer_name",
                    "rfq_no_project_name" :"project_details"
                    
                  
                },
				# "validation": {"docstatus": ["=", 1]},
			},
			"Quotation Item": {
				"doctype": "D Request Table",
				"field_map": {"item_name": "item_name", "qty": "quantity", "description": "description"},
			},
		},
		target_doc,
	)

	return doc


@frappe.whitelist()
def create_design_request(source_name, target_doc=None):
	doc = get_mapped_doc(
		"Quotation",
		source_name,
		{
			"Quotation": {
				"doctype": "Design Request",
				"field_map": {"name" :"quotation",
                    "contractor" :"contractor",
                    "client" :"client",
                    "consultant" :"contractor",
                    "employee" :"sales_person",
                    "rfq_no_project_name" :"project_name"
                    
                  
                },
				# "validation": {"docstatus": ["=", 1]},
			},
			"Quotation Item": {
				"doctype": "D Request Table",
				"field_map": {"item_name": "item_name", "qty": "quantity", "description": "description"},
			},
		},
		target_doc,
	)

	return doc


@frappe.whitelist()
def create_opportunity(source_name, target_doc=None):
	doc = get_mapped_doc(
		"Quotation",
		source_name,
		{
			"Quotation": {
				"doctype": "Opportunity",
				"field_map": {"name" :"custom_quotation",
					# "employee": "custom_sales_person_employee",
					# "employee_name": "custom_employee_name",
                    "custom_sales_person" :"custom_sales_person_user",
                    "custom_date_of_enquiry" :"custom_date_of_enquiry",
                    # "priority" :"custom_priority",
                    "scope_of_work" :"custom_scope_of_work",
                    "rfq_no_project_name" :"rfq_no_project_name",
                    "market_segment" :"market_segment",
                    "country": "custom_country",
                    "delivery_terms_conditions": "custom_delivery_terms_conditions",
                    "delivery_terms": "custom_delivery_terms",
                    "quotation_lost": "custom_quotation_lost",
                    "quotation_lost_user_update": "custom_quotation_lost_user_update",
                    "quotation_lost_reason": "custom_quotation_lost_reason",
                    "next_steps": "custom_next_steps",
                    "date_of_next_step": "custom_date_of_next_step",
                    "factory_visit_required": "custom_factory_visit_required",
                    "current_stage": "custom_current_stage",
                    "current_challenge": "custom_current_challenge",
                    "opportunity_owner": "opportunity_owner",
                    "territory": "territory",
                    # "bs_priority_quotation_information_link": "custom_bs_priority_quotation_information_link",
                    "currency": "currency",
                    "net_total": "opportunity_amount"
                    
                },
				# "validation": {"docstatus": ["=", 1]},
			},
		},
		target_doc,
	)
	doc.status = "Quotation"

	return doc