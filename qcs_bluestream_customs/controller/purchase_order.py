import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt


@frappe.whitelist()
def create_shipping_tracker(source_name, target_doc=None, skip_item_mapping=False):
	
	purchase_order_items = frappe.get_all("Purchase Order Item",filters = dict(parent=source_name), fields = ["name"], order_by = "idx")

	def get_shipping_tracker_item_count(purchase_order_items):
		return frappe._dict(
			frappe.db.sql(
				"""
			select purchase_order_item, sum(qty)
			from `tabShipping Tracker Item`
			where docstatus = 1
			and purchase_order_item = %s group by purchase_order_item
		""",
				purchase_order_items,
			)
		)
	
	def update_item(source, target, source_parent):
		st_qty = get_shipping_tracker_item_count(source.name)
		qty = st_qty.get(source.name, 0)
		target.qty = flt(source.qty) - flt(qty)
	
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
		def condition(doc):
			st_qty = get_shipping_tracker_item_count(doc.name)
			qty = st_qty.get(doc.name, 0)
			if (doc.qty <= qty):
				return False
			else:
				return True
		
		mapper["Purchase Order Item"] = {
			"doctype": "Shipping Tracker Item",
			"field_map": {
					"item_code": "item_code",
					"description": "description",
                    "material_request": "material_request",
                    "name": "purchase_order_item",
                    "parent": "purchase_order",
			},
			"postprocess": update_item,
			"condition": condition,
		}

	target_doc = get_mapped_doc("Purchase Order", source_name, mapper, target_doc)
	
	return target_doc

