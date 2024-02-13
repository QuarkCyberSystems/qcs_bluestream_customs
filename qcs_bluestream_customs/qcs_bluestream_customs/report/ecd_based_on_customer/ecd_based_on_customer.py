# Copyright (c) 2024, QCS and contributors
# For license information, please see license.txt

import frappe
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from datetime import datetime



def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data



def get_columns(filters):
	columns = [
		{
			"label": "Customer Name",
			"fieldname": "customer_name",
			"fieldtype": "Data",
			"width": 200,
		}
	]
	
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	status = filters.get("status")
	company = filters.get("company")
 
	date = []
	quo_doc = frappe.get_all("Quotation", filters={"transaction_date":["between", [from_date, to_date]], "company": company, "quotation_status": status, "docstatus": 1})
	for i in quo_doc:
		doc = frappe.get_doc("Quotation", i)
		date.append(doc.expected_closure_date)
		
	without_dup_list = list(set(date))

	columns.extend([{
		"label": str(date_item),
		"fieldname": str(date_item),
		"fieldtype": "Currency",
		"width": 150,
	} for date_item in without_dup_list])
	
	columns.append({
		"label": "Total Amount",
		"fieldname": "total_amount",
		"fieldtype": "Currency",
		"width": 150,
	})
	return columns


 
def get_data(filters):
	data = []
	
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	status = filters.get("status")
	company = filters.get("company")
 
	customer = []
	quo_doc = frappe.get_all("Quotation", filters={"transaction_date":["between", [from_date, to_date]], "company": company, "quotation_status": status, "docstatus": 1})
	
	for i in quo_doc:
		doc = frappe.get_doc("Quotation", i)
		customer.append(doc.customer_name)
	
	with_out_dub_cus = list(set(customer))
	
	for cus in with_out_dub_cus:
		row = {"customer_name": cus}
		total_mo = []
		quo_doc_per_customer = frappe.get_all("Quotation", filters={"transaction_date":["between", [from_date, to_date]], "company": company, "quotation_status": status, "customer_name": cus, "docstatus": 1}, fields=["name", "grand_total", "expected_closure_date"])
  
		grand_total_per_date = {}
		
		for i in quo_doc_per_customer:
			doc = frappe.get_doc("Quotation", i.name)
			date = doc.expected_closure_date
			grand_total = doc.grand_total
			
			if date not in grand_total_per_date:
				grand_total_per_date[date] = grand_total
			else:
				grand_total_per_date[date] += grand_total
		
		for date, total in grand_total_per_date.items():
			row[str(date)] = total
			total_mo.append(total)
		
		row["total_amount"] = sum(total_mo)
		data.append(row)
  
	return data