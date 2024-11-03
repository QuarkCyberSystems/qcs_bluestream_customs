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
                "field_map": {
                    "name": "custom_opportunity",
                    "status": "status",
                    "custom_sales_person_user": "sales_person_custom",
                    "custom_scope_of_work": "scope_of_work_1",
                    "custom_project": "custom_project_id",
                    "custom_project_name": "custom_project_name",
                    "custom_parent_project": "custom_parent_project",
                    "custom_parent_project_name": "custom_parent_project_name",
                    "custom_date_of_enquiry": "custom_date_of_enquiry"
                },
                # "validation": {"docstatus": ["=", 1]},
            },
        },
        target_doc,
    )

    return doc
