# Copyright (c) 2024, QCS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class SamplingWorkOrder(Document):
	def validate(self):
		self.actual_operating_cost = 0
		self.total_material_cost = 0
		for item in self.operations:
			item.actual_operating_cost = item.hour_rate / 60 * item.time_in_mins
			self.actual_operating_cost += item.actual_operating_cost
		for item in self.required_items:
			self.total_material_cost += item.amount
		self.total_cost = self.actual_operating_cost + self.total_material_cost
		self.set_status()

	def on_submit(self):
		st = []
		jc = []
		if (frappe.get_all("Stock Entry", filters={"custom_sampling_work_order": self.name}, fields=['name', 'docstatus'])):
			doc = frappe.get_all("Stock Entry", filters={"custom_sampling_work_order": self.name}, fields=['name', 'docstatus'])
			for i in doc:
				if (i.get("docstatus") != 1):
					st.append(i.get("name"))

		if st:
			pass
			# frappe.throw("Please Check Stock Entry. Stock Entery Not Submitted")
		if jc:
			frappe.throw("Please Check Job Card. Job Card Not Submitted")

		self.create_bom()
		self.create_ste()

	def create_bom(self):
		bom = frappe.new_doc("BOM")
		bom.company = self.company
		bom.item = self.production_item
		bom.quantity = self.qty
		bom.item_uom = self.item_uom
		bom.currency = self.currency
		bom.rm_cost_as_per = "Valuation Rate"
		bom.with_operations = 1
		bom.transfer_material_against = "Work Order"
		for item in self.operations:
			bom.append("operations", {
				"operation": item.operation,
				"workstation": item.workstation,
				"time_in_mins": item.time_in_mins
			})
		for item in self.required_items:
			bom.append("items", {
				"item_code": item.item_code,
				"uom": item.uom,
				"qty": item.qty,
				"rate": 0,
				"include_item_in_manufacturing": 1
			})
		for item in self.scrap_items:
			bom.append("scrap_items", {
				"item_code": item.item_code,
				"stock_uom": item.stock_uom,
				"stock_qty": item.stock_qty,
				"rate": item.rate
			})
		bom.is_active = 1
		bom.is_default = 1
		bom.save()
		self.finished_bom = bom.name
		bom.submit()

	def create_ste(self):
		bom = frappe.get_doc("BOM", self.finished_bom)
		# frappe.errprint(self.name)
		ste = frappe.new_doc("Stock Entry")
		ste.naming_series = "MAT-STE-.YYYY.-"
		ste.company = self.company
		ste.stock_entry_type = "Manufacture"
		ste.from_bom = 1
		ste.use_multi_level_bom = 1
		ste.bom_no = self.finished_bom
		ste.fg_completed_qty = self.qty
		ste.from_warehouse = self.wip_warehouse
		ste.to_warehouse = self.fg_warehouse
		ste.custom_sampling_work_order = self.name
		ste.cost_center_qcs = self.cost_center
		ste.order_no = self.sales_order
		# ste.get_items()
		# frappe.errprint(ste.items)
		for item in bom.items:
			ste.append("items", {
				"item_code": item.item_code,
				"qty": item.qty,
				"uom": item.uom,
				"s_warehouse": self.wip_warehouse,
				"t_warehouse": ""
			})
		ste.append("items", {
			"t_warehouse": ste.to_warehouse,
			"item_code": bom.item,
			"qty": bom.quantity,
			"uom": bom.uom,
			"is_finished_item": 1,
			"cost_center": self.cost_center
		})
		for item in bom.scrap_items:
			ste.append("items", {
				"t_warehouse": ste.to_warehouse,
				"item_code": item.item_code,
				"qty": item.stock_qty,
				"uom": item.stock_uom,
				"basic_rate": item.rate,
				"is_scrap_item": 1
			})
		# ste.append("additional_costs", {
		# 	"expense_account": frappe.get_value("Company", self.company, "default_labour_charge"),
		# 	"description": "Labour Costs",
		# 	"amount": self.actual_operating_cost
		# })

		ste.save()

	def set_status(self):
		if self.operations:
			self.jc_status = "In Process"
		if self.docstatus == 1:
			self.jc_status = "Completed"
   
   
   
@frappe.whitelist()
def create_jc(source_name, target_doc=None):
	doc = frappe.get_doc("Sampling Work Order", source_name)

	target_doc = get_mapped_doc(
		"Sampling Work Order",
		source_name,
		{
			"Sampling Work Order": {
				"doctype": "Job Card",
				#"validation": {"status": ["=", "Order Verified"]},
				"field_map": {
					"company": "company",
					"custom_sampling_work_order": "name",
					"qty": "for_quantity",
					# "order_form_qcs": "order_form_qcs"
				
				}
				},
		},
		target_doc
	)
	return target_doc
