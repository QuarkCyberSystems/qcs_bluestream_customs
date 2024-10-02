import frappe
from frappe import _
from frappe.utils import flt, today, date_diff


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters):
    columns = [
        {
            "label": _("Estimation No"),
            "options": "Estimation",
            "fieldname": "estimation_no",
            "fieldtype": "Link",
            "width": 140,
        },
        {
            "label": _("Quotation No"),
            "options": "Quotation",
            "fieldname": "quotation_no",
            "fieldtype": "Link",
            "width": 140,
        },
        {
            "label": _("Quotation Date"),
            "fieldname": "quotation_date",
            "fieldtype": "Data",
            "width": 140,
        },
        
        {
            "label": _("Client"),
            "fieldname": "client",
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "label": _("Contractor"),
            "fieldname": "contractor",
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "label": _("Turn Around Time Date"),
            "fieldname": "turn_around_time_date",
            "fieldtype": "Date",
            "width": 140,
        },
        {
            "label": _("Delayed Days"),
            "fieldname": "delayed_days",
            "fieldtype": "Int",
            "width": 140,
        },
        {
            "label": _("Overdue Remarks"),
            "fieldname": "overdue_remarks",
            "fieldtype": "Data",
            "width": 140,
        },
    ]
    return columns


def get_data(filters):
    estimation_entries = get_estimation_entries(filters)
    records = []

    for est in estimation_entries:
        frappe.errprint(est)
        delayed_days = 0
        if est.status == "Overdue" and est.turn_around_time_date:
            delayed_days = date_diff(today(), est.turn_around_time_date)
        record = {
            "estimation_no": est.name,
            "quotation_no": est.quotation,
            "quotation_date": est.quotation_date,  
            "client": est.client,
            "contractor": est.contractor,
            "status": est.custom_turn_around_time_status,
            "turn_around_time_date": est.custom_turn_around_time_date,
            "delayed_days": delayed_days,
            "overdue_remarks": est.custom_remarks
        }
        records.append(record)

    return records


def get_estimation_entries(filters):
    parent = frappe.qb.DocType("Estimation")
    child = frappe.qb.DocType("D Request Table")

    query = (
        frappe.qb.from_(parent)
        .join(child).on(parent.name == child.parent)
        .select(
            parent.quotation,
            parent.quotation_date,
            parent.name,
            parent.client,
            parent.contractor,
            parent.custom_turn_around_time_status,
            parent.custom_turn_around_time_date,
            parent.custom_remarks
        )
        .where(parent.docstatus == filters.get("docstatus", 0))
    )

    if filters.get("estimation_no"):
        query = query.where(parent.name == filters.get("estimation_no"))
    if filters.get("quotation_no"):
        query = query.where(parent.quotation == filters.get("quotation_no"))

    return query.run(as_dict=True)
