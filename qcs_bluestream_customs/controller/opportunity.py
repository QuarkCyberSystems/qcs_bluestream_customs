import frappe
from frappe.model.mapper import get_mapped_doc


@frappe.whitelist()
def create_estimation(source_name, target_doc=None):
	doc = get_mapped_doc(
		"Opportunity",
		source_name,
		{
			"Opportunity": {
				"doctype": "Estimation",
				"field_map": {"name": "custom_opportunity",
                    "status": "status",
                    "custom_sales_person_user": "sales_person",
                    # "custom_sales_person_employee": "sales_person_employee",
                    # "custom_employee_name": "employee_name",
                    "custom_scope_of_work": "scope_of_work_1",
                    # "custom_priority": "priority",
                    "rfq_no_project_name": "project",
                    "custom_date_of_enquiry": "custom_date_of_enquiry"
                                  
                  
                },
				# "validation": {"docstatus": ["=", 1]},
			},
			
		},
		target_doc,
	)

	return doc

