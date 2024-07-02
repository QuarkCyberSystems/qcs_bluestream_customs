import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt


@frappe.whitelist()
def create_shipping_tracker(source_name, target_doc=None, skip_item_mapping=False):
	def update_item(source, target, source_parent):
		target.qty = flt(source.qty)
	
	mapper = {
		"Purchase Order": {
		    "doctype": "Shipping Tracker",
		    "field_map": {
				"supplier": "supplier"
				
 			},
		   "validation": {"docstatus": ["=", 1]}
		},
	
	}

	if not skip_item_mapping:
		mapper["Purchase Order Item"] = {
			"doctype": "Shipping Tracker Item",
			"field_map": {
					"item_code": "item_code",
					"description": "description",
                    "material_request": "material_request",
                    "name": "purchase_order_item",
                    "parent": "purchase_order",
			},
			"postprocess": update_item
		}

	target_doc = get_mapped_doc("Purchase Order", source_name, mapper, target_doc)
	
	return target_doc

