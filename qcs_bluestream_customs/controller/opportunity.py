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
                    "name": "opportunity",
                    # "status": "status",
                    "custom_sales_person": "sales_person_custom",
                    "custom_scope_of_work": "scope_of_work_1",
                    "custom_project": "project_id",
                    "custom_project_name": "project_name",
                    "custom_parent_project": "parent_project",
                    "custom_parent_project_name": "parent_project_name"
                },
                # "validation": {"docstatus": ["=", 1]},
            },
        },
        target_doc,
    )

    return doc
