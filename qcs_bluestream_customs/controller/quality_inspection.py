# Copyright (c) 2024, Quark Cyber Systems FZC
# For license information, please see license.txt


import frappe


def update_custom_quality_inspection_details(quality_inspection, method=None):
    if quality_inspection.reference_type == 'Job Card':
        job_card = frappe.get_doc('Job Card', quality_inspection.reference_name)
        work_order = frappe.get_doc('Work Order', job_card.work_order)
        sales_order = frappe.get_doc('Sales Order', work_order.sales_order)
        if quality_inspection.custom_operation != job_card.operation:
            quality_inspection.custom_operation = job_card.operation
        if quality_inspection.custom_work_order != job_card.work_order:
            quality_inspection.custom_work_order = job_card.work_order
        if work_order.sales_order:
            if quality_inspection.custom_sales_order != work_order.sales_order:
                quality_inspection.custom_sales_order = work_order.sales_order
            if quality_inspection.custom_customer != sales_order.customer:
                quality_inspection.custom_customer = sales_order.customer
        else:
            pass
    else:
        pass
