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
			"label": "Status",
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": "Customer Name",
			"fieldname": "customer_name",
			"fieldtype": "Data",
			"width": 200,
		}
	]
 
	query_filters = []
	if filters.get("employee"):
		query_filters.append(["employee", "=", filters.get("employee")])
	if filters.get("quotation_to") == "Customer":
		if filters.get("customer"):
			query_filters.append(["party_name", "=", filters.get("customer")])
	if filters.get("quotation_to") == "Lead":
		if filters.get("lead"):
			query_filters.append(["party_name", "=", filters.get("lead")])
	if filters.get("company"):
		query_filters.append(["company", "=", filters.get("company")])
	query_filters.append(["transaction_date", ">=", filters.get("from_date")])
	query_filters.append(["transaction_date", "<=", filters.get("to_date")])
	if filters.get("status"):
		query_filters.append(["quotation_status", "=", filters.get("status")])
	query_filters.append(["docstatus", "=", 1])
	
 
	date = []
	quo_doc = frappe.get_all("Quotation", filters=query_filters)
	for i in quo_doc:
		doc = frappe.get_doc("Quotation", i)
		date.append(doc.expected_closure_date)
		
	without_dup_list = sorted(list(set(date)))

	columns.extend([{
		"label": str(date_item.strftime('%d-%m-%Y')),
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
 
	if(filters.get("status")):
		query_filters = []
		if filters.get("employee"):
			query_filters.append(["employee", "=", filters.get("employee")])
		if filters.get("quotation_to") == "Customer":
			if filters.get("customer"):
				query_filters.append(["party_name", "=", filters.get("customer")])
		if filters.get("quotation_to") == "Lead":
			if filters.get("lead"):
				query_filters.append(["party_name", "=", filters.get("lead")])
		if filters.get("company"):
			query_filters.append(["company", "=", filters.get("company")])
		query_filters.append(["transaction_date", ">=", filters.get("from_date")])
		query_filters.append(["transaction_date", "<=", filters.get("to_date")])
		if filters.get("status"):
			query_filters.append(["quotation_status", "=", filters.get("status")])
		query_filters.append(["docstatus", "=", 1])
		
		customer = []
		quo_doc = frappe.get_all("Quotation", filters=query_filters)
		
		for i in quo_doc:
			doc = frappe.get_doc("Quotation", i)
			customer.append(doc.customer_name)
		
		with_out_dub_cus = sorted(list(set(customer)))
		
		status_row = {"status": filters.get("status")}
		over_all_amount = {}
		overall_total_mo = []
		
		for cus in with_out_dub_cus:
			row = {"customer_name": cus}
			total_mo = []
	
			query_filters1 = []
			if filters.get("employee"):
				query_filters1.append(["employee", "=", filters.get("employee")])
			if filters.get("company"):
				query_filters1.append(["company", "=", filters.get("company")])
			query_filters1.append(["customer_name", "=", cus])
			query_filters1.append(["transaction_date", ">=", filters.get("from_date")])
			query_filters1.append(["transaction_date", "<=", filters.get("to_date")])
			if filters.get("status"):
				query_filters.append(["quotation_status", "=", filters.get("status")])
			query_filters1.append(["docstatus", "=", 1])
	
			quo_doc_per_customer = frappe.get_all("Quotation", filters=query_filters1, fields=["name", "grand_total", "expected_closure_date"])
	
			grand_total_per_date = {}
			
			for i in quo_doc_per_customer:
				doc = frappe.get_doc("Quotation", i.name)
				date = doc.expected_closure_date
				grand_total = doc.grand_total
				
				if date not in grand_total_per_date:
					grand_total_per_date[date] = grand_total
				else:
					grand_total_per_date[date] += grand_total
    #  overall
				if date not in over_all_amount:
					over_all_amount[date] = grand_total
				else:
					over_all_amount[date] += grand_total
	#####		
			for date, total in grand_total_per_date.items():
				row[str(date)] = total
				total_mo.append(total)
			
			row["total_amount"] = sum(total_mo)
			data.append(row)
   
		for date, total in over_all_amount.items():
			status_row[str(date)] = total
			overall_total_mo.append(total)
    
		status_row["total_amount"] = sum(overall_total_mo)
		data.append(status_row)
  
	else:
     
		set_sastus = ["Quotation Pending", "Under Negotiation", "PO Confirmed", "Set as lost", "On track", "Delayed", "Prolonged Delay", "Order Closed", "Lost", "Cancelled"]
		for s_status in set_sastus:
			query_filters = []
			if filters.get("employee"):
				query_filters.append(["employee", "=", filters.get("employee")])
			if filters.get("quotation_to") == "Customer":
				if filters.get("customer"):
					query_filters.append(["party_name", "=", filters.get("customer")])
			if filters.get("quotation_to") == "Lead":
				if filters.get("lead"):
					query_filters.append(["party_name", "=", filters.get("lead")])
			if filters.get("company"):
				query_filters.append(["company", "=", filters.get("company")])
			query_filters.append(["transaction_date", ">=", filters.get("from_date")])
			query_filters.append(["transaction_date", "<=", filters.get("to_date")])
			query_filters.append(["quotation_status", "=", s_status])
			query_filters.append(["docstatus", "=", 1])
			
			customer = []
			quo_doc = frappe.get_all("Quotation", filters=query_filters)
			
			for i in quo_doc:
				doc = frappe.get_doc("Quotation", i)
				customer.append(doc.customer_name)
			
			with_out_dub_cus = sorted(list(set(customer)))
   
			status_row = {"status": s_status}
			over_all_amount = {}
			overall_total_mo = []
			
			for cus in with_out_dub_cus:
				row = {"customer_name": cus}
				total_mo = []
		
				query_filters1 = []
				if filters.get("employee"):
					query_filters1.append(["employee", "=", filters.get("employee")])
				if filters.get("company"):
					query_filters1.append(["company", "=", filters.get("company")])
				query_filters1.append(["customer_name", "=", cus])
				query_filters1.append(["transaction_date", ">=", filters.get("from_date")])
				query_filters1.append(["transaction_date", "<=", filters.get("to_date")])
				query_filters.append(["quotation_status", "=", s_status])
				query_filters1.append(["docstatus", "=", 1])
		
				quo_doc_per_customer = frappe.get_all("Quotation", filters=query_filters1, fields=["name", "grand_total", "expected_closure_date"])
		
				grand_total_per_date = {}
				
				for i in quo_doc_per_customer:
					doc = frappe.get_doc("Quotation", i.name)
					date = doc.expected_closure_date
					grand_total = doc.grand_total
					
					if date not in grand_total_per_date:
						grand_total_per_date[date] = grand_total
					else:
						grand_total_per_date[date] += grand_total
        #  overall
					if date not in over_all_amount:
						over_all_amount[date] = grand_total
					else:
						over_all_amount[date] += grand_total
		######		
				for date, total in grand_total_per_date.items():
					row[str(date)] = total
					total_mo.append(total)
				
				row["total_amount"] = sum(total_mo)
				data.append(row)
    
			for date, total in over_all_amount.items():
				status_row[str(date)] = total
				overall_total_mo.append(total)
		
			status_row["total_amount"] = sum(overall_total_mo)
			data.append(status_row)
	
	return data