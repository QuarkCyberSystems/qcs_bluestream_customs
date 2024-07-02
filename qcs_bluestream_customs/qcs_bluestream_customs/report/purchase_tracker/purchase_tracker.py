# Copyright (c) 2024, QCS and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    columns = [
        {
            "label": _("Material Request No"),
            "options": "Material Request",
            "fieldname": "material_request_no",
            "fieldtype": "Link",
            "width": 140,
        },
        {
            "label": _("Purchase Order"),
            "options": "Purchase Order",
            "fieldname": "purchase_order",
            "fieldtype": "Link",
            "width": 140,
        },
        {
            "label": _("Item"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 150,
        },
        {
            "label": _("Item Name"),
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Quantity"),
            "fieldname": "quantity",
            "fieldtype": "Float",
            "width": 140,
        },
        {
            "label": _("Unit of Measure"),
            "options": "UOM",
            "fieldname": "unit_of_measurement",
            "fieldtype": "Link",
            "width": 140,
        },
    ]
    return columns

def apply_filters_on_query(filters, parent, child, query):
    if filters.get("company"):
        query = query.where(parent.company == filters.get("company"))

    if filters.get("from_date"):
        query = query.where(parent.transaction_date >= filters.get("from_date"))

    if filters.get("to_date"):
        query = query.where(parent.transaction_date <= filters.get("to_date"))

    return query

def get_data(filters):
    purchase_order_entry = get_po_entries(filters)
    mr_records, _ = get_mapped_mr_details(filters)
    procurement_record = []

    for po in purchase_order_entry:
        # fetch material records linked to the purchase order item
        material_requests = mr_records.get(po.material_request_item, [{}])

        for mr_record in material_requests:
            procurement_detail = {
                "material_request_no": po.material_request,
                "purchase_order": po.parent,
                "item_code": po.item_code,
                "item_name":po.item_name,
                "quantity": flt(po.qty),
                "unit_of_measurement": po.stock_uom,
            }
            procurement_record.append(procurement_detail)

    return procurement_record

def get_mapped_mr_details(filters):
    mr_records = {}
    parent = frappe.qb.DocType("Material Request")
    child = frappe.qb.DocType("Material Request Item")

    query = (
        frappe.qb.from_(parent)
        .from_(child)
        .select(
            child.name,
            child.parent,
            child.item_code,
            child.item_name,
            child.qty,
            child.uom,
        )
        .where((parent.per_ordered >= 0) & (parent.name == child.parent) & (parent.docstatus == 1))
    )
    query = apply_filters_on_query(filters, parent, child, query)

    mr_details = query.run(as_dict=True)

    for record in mr_details:
        mr_records.setdefault(record.name, []).append(frappe._dict(record))

    return mr_records, []

def get_po_entries(filters):
    parent = frappe.qb.DocType("Purchase Order")
    child = frappe.qb.DocType("Purchase Order Item")

    query = (
        frappe.qb.from_(parent)
        .from_(child)
        .select(
            child.parent,
            child.material_request,
            child.material_request_item,
            child.item_code,
            child.item_name,
            child.qty,
            child.stock_uom,
        )
        .where(
            (parent.docstatus == 1)
            & (parent.name == child.parent)
            & (parent.status.notin(("Closed", "Completed", "Cancelled")))
        )
        .groupby(parent.name, child.material_request_item)
    )
    query = apply_filters_on_query(filters, parent, child, query)

    return query.run(as_dict=True)
