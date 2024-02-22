# Copyright (c) 2024, QCS and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime
from collections import defaultdict
from datetime import datetime, timedelta



def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns(filters)
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart


def get_columns(filters):
	columns = [
		{
			"label": "Date",
			"fieldname": "date",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": "Grand Total",
			"fieldname": "grand_total",
			"fieldtype": "Currency",
			"width": 200,
		},
		{
			"label": "Monthly Sales Target",
			"fieldname": "target",
			"fieldtype": "Currency",
			"width": 200,
		},
		{
			"label": "Balance",
			"fieldname": "bal",
			"fieldtype": "Currency",
			"width": 200,
		},
	]
	return columns


def get_data(filters):
	
	query_filters = []
	query_filters.append(["company", "=", filters.get("company")])
	query_filters.append(["transaction_date", ">=", filters.get("from_date")])
	query_filters.append(["transaction_date", "<=", filters.get("to_date")])
	query_filters.append(["docstatus", "=", 1])
 
	company = frappe.get_doc("Company", filters.get("company"))
	target = company.monthly_sales_target
	

	sales_orders = frappe.get_all(
		"Sales Order",
		filters=query_filters,
		fields=["transaction_date", "grand_total"]
	)
 
	date1 = []
	for order in sales_orders:
		date = order.transaction_date.strftime('%b %Y')
		date1.append(date)
		
	date1 = [datetime.strptime(d, '%b %Y') for d in date1]

	without_dup_set = set()
	without_dup_list = []
	for d in date1:
		date_str = d.strftime('%b %Y')
		if date_str not in without_dup_set:
			without_dup_set.add(date_str)
			without_dup_list.append(date_str)

	without_dup_list.sort(key=lambda x: datetime.strptime(x, '%b %Y'))
 
	grand_total_per_date = {}
	for al_date in without_dup_list:
		for order in sales_orders:
			date = order.transaction_date.strftime('%b %Y')
			if (date == al_date):
				if date not in grand_total_per_date:
					grand_total_per_date[date] = order.grand_total
				else:
					grand_total_per_date[date] += order.grand_total

	result = [{"date": dates, "grand_total": total, "target": target, "bal": total-target} for dates, total in grand_total_per_date.items()]
	return result


def get_chart_data(data):
	sum_target = sum(row["target"] for row in data)
	sum_grand_total = sum(row["grand_total"] for row in data)

	if (sum_grand_total > sum_target):
		ex = sum_grand_total - sum_target
		return {
			"data": {"labels": ['Grand Total', 'excess'], "datasets": [{'values': [sum_grand_total, ex]}]},
			"type": "percentage",
		}
	else:
		bal = sum_target - sum_grand_total
		return {
			"data": {"labels": ['Grand Total', 'Sales Target Balance'], "datasets": [{'values': [sum_grand_total, bal]}]},
			"type": "percentage",
		}