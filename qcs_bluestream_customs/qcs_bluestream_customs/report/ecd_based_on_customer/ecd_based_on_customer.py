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
		},
		{
			"label": "Quotation",
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Quotation",
			"width": 200,
		},
		{
			"label": "RFQ No / Project Name",
			"fieldname": "rfq_no_project_name",
			"fieldtype": "Data",
			"width": 200,
		}
	]
 
	if filters.get("jih__tender"):
		columns.append({
			"label": "JIH / Tender",
			"fieldname": "jih__tender",
			"fieldtype": "Data",
			"width": 200,
		})
 
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
	query_filters.append(["expected_closure_date", ">=", filters.get("from_date")])
	query_filters.append(["expected_closure_date", "<=", filters.get("to_date")])
	if filters.get("status"):
		query_filters.append(["quotation_status", "=", filters.get("status")])
	query_filters.append(["status", "not in", ["Cancelled", "Lost"]])
	if filters.get("jih__tender"):
		query_filters.append(["jih__tender", "=", filters.get("jih__tender")])
	query_filters.append(["docstatus", "=", 1])
	
 
	date = []
	quo_doc = frappe.get_all("Quotation", filters=query_filters)
	for i in quo_doc:
		doc = frappe.get_doc("Quotation", i)
		ecd = doc.expected_closure_date
		date.append(ecd.strftime('%b %Y'))
		
	# without_dup_list = sorted(list(set(date)))
	date = [datetime.strptime(d, '%b %Y') for d in date]

	without_dup_set = set()
	without_dup_list = []
	for d in date:
		date_str = d.strftime('%b %Y')
		if date_str not in without_dup_set:
			without_dup_set.add(date_str)
			without_dup_list.append(date_str)

	without_dup_list.sort(key=lambda x: datetime.strptime(x, '%b %Y'))
 
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
		query_filters.append(["expected_closure_date", ">=", filters.get("from_date")])
		query_filters.append(["expected_closure_date", "<=", filters.get("to_date")])
		if filters.get("status"):
			query_filters.append(["quotation_status", "=", filters.get("status")])
		query_filters.append(["status", "not in", ["Cancelled", "Lost"]])
		if filters.get("jih__tender"):
			query_filters.append(["jih__tender", "=", filters.get("jih__tender")])
		query_filters.append(["docstatus", "=", 1])
		
		customer = []
		quo_doc = frappe.get_all("Quotation", filters=query_filters)
		
		for i in quo_doc:
			doc = frappe.get_doc("Quotation", i)
			customer.append(doc.customer_name)
		
		with_out_dub_cus = sorted(list(set(customer)))
		
		status_row = {"status": filters.get("status")}
		status_row1 = {"status": "Grand Total"}
		over_all_amount = {}
		overall_total_mo = []
		status_values = []
		quotation_values = []
		
		for cus in with_out_dub_cus:
			# row = {"customer_name": cus}
			customer_link = f'''
				<a href= "/app/quotation?company={filters.get("company")}&quotation_status={filters.get("status")}&docstatus=1&customer_name={cus}&expected_closure_date=%5B%22Between%22%2C%5B%22{filters.get("from_date")}%22%2C%22{filters.get("to_date")}%22%5D%5D">{cus}</a>
				'''
			row = {"customer_name": customer_link}
			total_mo = []
	
			query_filters1 = []
			if filters.get("employee"):
				query_filters1.append(["employee", "=", filters.get("employee")])
			if filters.get("company"):
				query_filters1.append(["company", "=", filters.get("company")])
			query_filters1.append(["customer_name", "=", cus])
			query_filters1.append(["expected_closure_date", ">=", filters.get("from_date")])
			query_filters1.append(["expected_closure_date", "<=", filters.get("to_date")])
			if filters.get("status"):
				query_filters1.append(["quotation_status", "=", filters.get("status")])
			query_filters1.append(["status", "not in", ["Cancelled", "Lost"]])
			if filters.get("jih__tender"):
				query_filters1.append(["jih__tender", "=", filters.get("jih__tender")])
			query_filters1.append(["docstatus", "=", 1])
	
			quo_doc_per_customer = frappe.get_all("Quotation", filters=query_filters1, fields=["name", "grand_total", "expected_closure_date", "customer_name", "jih__tender", "rfq_no_project_name"])
	
			grand_total_per_date = {}
			for i in quo_doc_per_customer:
				doc = frappe.get_doc("Quotation", i.get("name"))
				date1 = doc.expected_closure_date
				grand_total = doc.grand_total
				
				date = date1.strftime('%b %Y')
	
				quot_row = {"name": i.get("name"), "jih__tender": i.get("jih__tender"), "rfq_no_project_name": i.get("rfq_no_project_name"), "cus_name": i.get("customer_name"), "indent": 2, date: i.get("grand_total"), "total_amount": i.get("grand_total")}
				quotation_values.append(quot_row)
	
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
			row["indent"] = 1
			row["cus"] = cus
			status_values.append(row)
   
		for date, total in over_all_amount.items():
			status_row[str(date)] = total
			status_row1[str(date)] = total
			overall_total_mo.append(total)
	
		status_row["total_amount"] = sum(overall_total_mo)
		status_row["indent"] = 0
		data.append(status_row)
		
		status_row1["total_amount"] = sum(overall_total_mo)
		status_row1["indent"] = 1
  
		for vlues in status_values:
			data.append(vlues)
			for quot_val in quotation_values:
				if (vlues.get("cus") == quot_val.get("cus_name")):
					data.append(quot_val)
	 
		frappe.errprint(status_row1)
		data.append(status_row1)
				
  
	else:
	 
		set_sastus = ["Quotation Pending", "On track", "Delayed", "Prolonged Delay", "Under Negotiation"]
		status_row1 = {"status": "Grand Total"}
		over_all_amount1 = {}
		overall_total_mo1 = []
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
			query_filters.append(["expected_closure_date", ">=", filters.get("from_date")])
			query_filters.append(["expected_closure_date", "<=", filters.get("to_date")])
			query_filters.append(["quotation_status", "=", s_status])
			query_filters.append(["docstatus", "=", 1])
			query_filters.append(["status", "not in", ["Cancelled", "Lost"]])
			if filters.get("jih__tender"):
				query_filters.append(["jih__tender", "=", filters.get("jih__tender")])
			
			customer = []
			quo_doc = frappe.get_all("Quotation", filters=query_filters)
			
			for i in quo_doc:
				doc = frappe.get_doc("Quotation", i)
				customer.append(doc.customer_name)
			
			with_out_dub_cus = sorted(list(set(customer)))
   
			status_row = {"status": s_status}
			over_all_amount = {}
			overall_total_mo = []
			status_values = []
			quotation_values = []
			
			for cus in with_out_dub_cus:
				# row = {"customer_name": cus}
				customer_link = f'''
				<a href= "/app/quotation?company={filters.get("company")}&quotation_status={s_status}&docstatus=1&customer_name={cus}&expected_closure_date=%5B%22Between%22%2C%5B%22{filters.get("from_date")}%22%2C%22{filters.get("to_date")}%22%5D%5D">{cus}</a>
				'''
				row = {"customer_name": customer_link}
				total_mo = []
		
				query_filters1 = []
				if filters.get("employee"):
					query_filters1.append(["employee", "=", filters.get("employee")])
				if filters.get("company"):
					query_filters1.append(["company", "=", filters.get("company")])
				query_filters1.append(["customer_name", "=", cus])
				query_filters1.append(["expected_closure_date", ">=", filters.get("from_date")])
				query_filters1.append(["expected_closure_date", "<=", filters.get("to_date")])
				query_filters1.append(["quotation_status", "=", s_status])
				query_filters1.append(["status", "not in", ["Cancelled", "Lost"]])
				query_filters1.append(["docstatus", "=", 1])
				if filters.get("jih__tender"):
					query_filters1.append(["jih__tender", "=", filters.get("jih__tender")])
		
				quo_doc_per_customer = frappe.get_all("Quotation", filters=query_filters1, fields=["name", "grand_total", "expected_closure_date", "customer_name", "jih__tender", "rfq_no_project_name"])
		
				grand_total_per_date = {}
				
				for i in quo_doc_per_customer:
					doc = frappe.get_doc("Quotation", i.name)
					date1 = doc.expected_closure_date
					grand_total = doc.grand_total
					
					date = date1.strftime('%b %Y')
					quot_row = {"name": i.get("name"), "jih__tender": i.get("jih__tender"), "rfq_no_project_name": i.get("rfq_no_project_name"), "cus_name": i.get("customer_name"), "indent": 2, date: i.get("grand_total"), "total_amount": i.get("grand_total")}
					quotation_values.append(quot_row)
	
					if date not in grand_total_per_date:
						grand_total_per_date[date] = grand_total
					else:
						grand_total_per_date[date] += grand_total
		#  overall
					if date not in over_all_amount:
						over_all_amount[date] = grand_total
					else:
						over_all_amount[date] += grand_total
	  
					if date not in over_all_amount1:
						over_all_amount1[date] = grand_total
					else:
						over_all_amount1[date] += grand_total
	  
		######	
				for date, total in grand_total_per_date.items():
					row[str(date)] = total
					total_mo.append(total)
				
				row["total_amount"] = sum(total_mo)
				row["indent"] = 1
				row["cus"] = cus
				status_values.append(row)
	
			for date, total in over_all_amount.items():
				status_row[str(date)] = total
				overall_total_mo.append(total)
	
		
			status_row["total_amount"] = sum(overall_total_mo)
			status_row["indent"] = 0
			data.append(status_row)
   
   
			for vlues in status_values:
				data.append(vlues)
				for quot_val in quotation_values:
					if (vlues.get("cus") == quot_val.get("cus_name")):
						data.append(quot_val)
	  
		for date, total in over_all_amount1.items():
			status_row1[str(date)] = total
			overall_total_mo1.append(total)
	  
		status_row1["total_amount"] = sum(overall_total_mo1)
		status_row1["indent"] = 0
		data.append(status_row1)

	return data