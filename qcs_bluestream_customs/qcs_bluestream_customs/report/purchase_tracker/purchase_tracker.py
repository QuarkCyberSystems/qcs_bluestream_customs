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
            "label": _("Shipping Tracker"),
            "options": "Shipping Tracker",
            "fieldname": "shipping_tracker",
            "fieldtype": "Link",
            "width": 140,
        },
        {
            "label": _("Supplier"),
            "options": "Supplier",
            "fieldname": "supplier",
            "fieldtype": "Link",
            "width": 140,
        },
        {
            "label": _("Item Code"),
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
        {
            "label": _("Shipment Mode"),
            "fieldname": "shipment_mode",
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "label": _("Status"),
            "fieldname": "status_of_the_shipment",
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "label": _("Estimated Timed Dispatch"),
            "fieldname": "estimated_timed_dispatch",
            "fieldtype": "Date",
            "width": 140,
        },
        {
            "label": _("Estimated Shipment Date"),
            "fieldname": "estimated_shipment_date",
            "fieldtype": "Date",
            "width": 140,
        },
        {
            "label": _("Actual Dispatch Date"),
            "fieldname": "actual_dispatch_date",
            "fieldtype": "Date",
            "width": 140,
        },
        {
            "label": _("Actual Arrival Date"),
            "fieldname": "actual_arrival_date",
            "fieldtype": "Date",
            "width": 140,
        }
    ]
    return columns


def apply_filters_on_query(filters, parent, child, query):
    query = query.where(parent.docstatus == 0)
    return query


def get_data(filters):
    shipping_tracker_entry = get_st_entries(filters)
    po_records, _ = get_mapped_po_details(filters)
    procurement_record = []

    for st in shipping_tracker_entry:
        purchase_orders = po_records.get(st.purchase_order_item, [{}])

        for po_record in purchase_orders:
            procurement_detail = {
                "material_request_no": st.material_request,
                "purchase_order": st.purchase_order,
                "shipping_tracker": st.parent,
                "supplier": st.supplier,
                "item_code": st.item_code,
                "item_name": st.item_name,
                "quantity": flt(st.qty),
                "unit_of_measurement": st.uom,
                "shipment_mode": st.shipment_mode,
                "status_of_the_shipment": st.status_of_the_shipment,
                "estimated_timed_dispatch": st.estimated_timed_dispatch,
                "estimated_shipment_date": st.estimated_shipment_date,
                "actual_dispatch_date": st.actual_dispatch_date,
                "actual_arrival_date": st.actual_arrival_date
            }
            procurement_record.append(procurement_detail)

    return procurement_record


def get_mapped_po_details(filters):
    po_records = {}
    parent = frappe.qb.DocType("Purchase Order")
    child = frappe.qb.DocType("Purchase Order Item")

    query = (
        frappe.qb.from_(parent)
        .join(child).on(parent.name == child.parent)
        .select(
            child.name,
            child.parent,
            child.item_code,
            child.item_name,
            child.qty,
            child.uom,
        )
        .where(parent.docstatus == 1)
    )

    query = apply_filters_on_query(filters, parent, child, query)

    po_details = query.run(as_dict=True)

    for record in po_details:
        po_records.setdefault(record.name, []).append(frappe._dict(record))

    return po_records, []


def get_st_entries(filters):
    parent = frappe.qb.DocType("Shipping Tracker")
    child = frappe.qb.DocType("Shipping Tracker Item")

    query = (
        frappe.qb.from_(parent)
        .join(child).on(parent.name == child.parent)
        .select(
            child.parent,
            child.material_request,
            child.purchase_order,
            child.purchase_order_item,
            parent.supplier,
            child.item_code,
            child.item_name,
            child.qty,
            child.uom,
            parent.shipment_mode,
            parent.status_of_the_shipment,
            parent.estimated_timed_dispatch,
            parent.estimated_shipment_date,
            parent.actual_dispatch_date,
            child.actual_arrival_date
        )
        .groupby(parent.name, child.purchase_order_item)
    )

    if filters.get("purchase_order"):
        query = query.where(child.purchase_order == filters.get("purchase_order"))

    query = apply_filters_on_query(filters, parent, child, query)

    return query.run(as_dict=True)
