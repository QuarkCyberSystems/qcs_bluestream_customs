# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# Import necessary modules
import datetime
import frappe
from dateutil.relativedelta import relativedelta
from frappe import _, scrub
from frappe.utils import get_first_day as get_first_day_of_month
from frappe.utils import get_first_day_of_week, get_quarter_start, getdate
from erpnext.accounts.utils import get_fiscal_year
from frappe.utils.nestedset import get_descendants_of
from frappe.query_builder.functions import CombineDatetime
from erpnext.stock.doctype.warehouse.warehouse import apply_warehouse_filter
from erpnext.stock.utils import is_reposting_item_valuation_in_progress


def execute(filters=None):
    is_reposting_item_valuation_in_progress()
    filters = frappe._dict(filters or {})
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data, None


def get_columns(filters):
    columns = [
        {"label": _("Item"), "options": "Item", "fieldname": "name", "fieldtype": "Link", "width": 140},
        {"label": _("Item Name"), "options": "Item", "fieldname": "item_name", "fieldtype": "Link", "width": 140},
        {"label": _("UOM"), "fieldname": "uom", "fieldtype": "Data", "width": 100},
    ]

    ranges = get_period_date_ranges(filters)

    for _dummy, end_date in ranges:
        period = get_period(end_date, filters)
        columns.append({"label": _(period), "fieldname": scrub(period), "fieldtype": "Float", "width": 120})

    return columns


def get_period_date_ranges(filters):
    from_date = round_down_to_nearest_frequency(filters.from_date, filters.range)
    to_date = getdate(filters.to_date)

    increment = {"Monthly": 1, "Quarterly": 3, "Half-Yearly": 6, "Yearly": 12}.get(filters.range, 1)

    periodic_daterange = []
    while from_date <= to_date:
        if filters.range == "Weekly":
            period_end_date = from_date + relativedelta(days=6)
        else:
            period_end_date = from_date + relativedelta(months=increment, days=-1)

        if period_end_date > to_date:
            period_end_date = to_date
        periodic_daterange.append([from_date, period_end_date])

        from_date = period_end_date + relativedelta(days=1)

    return periodic_daterange


def round_down_to_nearest_frequency(date: str, frequency: str) -> datetime.datetime:
    def _get_first_day_of_fiscal_year(date):
        fiscal_year = get_fiscal_year(date)
        return fiscal_year and fiscal_year[1] or date

    round_down_function = {
        "Monthly": get_first_day_of_month,
        "Quarterly": get_quarter_start,
        "Weekly": get_first_day_of_week,
        "Yearly": _get_first_day_of_fiscal_year,
    }.get(frequency, getdate)

    return round_down_function(date)


def get_period(posting_date, filters):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    if filters.range == "Weekly":
        period = _("Week {0} {1}").format(str(posting_date.isocalendar()[1]), str(posting_date.year))
    elif filters.range == "Monthly":
        period = _(str(months[posting_date.month - 1])) + " " + str(posting_date.year)
    elif filters.range == "Quarterly":
        period = _("Quarter {0} {1}").format(str(((posting_date.month - 1) // 3) + 1), str(posting_date.year))
    else:
        year = get_fiscal_year(posting_date, company=filters.company)
        period = str(year[2])

    return period


def get_periodic_data(entry, filters):
    expected_ranges = get_period_date_ranges(filters)
    expected_periods = [get_period(end_date, filters) for _start_date, end_date in expected_ranges]

    periodic_data = {}

    for d in entry:
        item_code = d.item_code
        period = get_period(d.posting_date, filters)
        warehouse = d.warehouse
        value = d.actual_qty

        if item_code not in periodic_data:
            periodic_data[item_code] = {period: {warehouse: value}}
        elif period not in periodic_data[item_code]:
            periodic_data[item_code][period] = {warehouse: value}
        elif warehouse not in periodic_data[item_code][period]:
            periodic_data[item_code][period][warehouse] = value
        else:
            periodic_data[item_code][period][warehouse] += value

    return periodic_data


def get_data(filters):
    data = []
    items = get_items(filters)
    sle = get_stock_ledger_entries(filters, items)
    item_details = get_item_details(items, sle)
    periodic_data = get_periodic_data(sle, filters)
    ranges = get_period_date_ranges(filters)

    for _dummy, item_data in item_details.items():
        row = {
            "name": item_data.name,
            "item_name": item_data.item_name,
            "item_group": item_data.item_group,
            "uom": item_data.stock_uom,
            "brand": item_data.brand,
        }

        for _start_date, end_date in ranges:
            period = get_period(end_date, filters)
            period_data = periodic_data.get(item_data.name, {}).get(period, {})

            total_qty = 0.0
            for warehouse, qty in period_data.items():
                total_qty += qty

            row[scrub(period)] = total_qty

        data.append(row)

    return data


def get_items(filters):
    if item_code := filters.get("item_code"):
        return [item_code]
    else:
        item_filters = {"is_stock_item": 1}
        if item_group := filters.get("item_group"):
            children = get_descendants_of("Item Group", item_group, ignore_permissions=True)
            item_filters["item_group"] = ("in", [*children, item_group])
        return frappe.get_all("Item", filters=item_filters, pluck="name", order_by=None)


def get_stock_ledger_entries(filters, items):
    sle = frappe.qb.DocType("Stock Ledger Entry")
    se = frappe.qb.DocType("Stock Entry")

    query = (
        frappe.qb.from_(sle)
        .select(
            sle.item_code,
            sle.warehouse,
            sle.posting_date,
            sle.actual_qty,
            sle.valuation_rate,
            sle.company,
            sle.voucher_type,
            sle.qty_after_transaction,
            sle.stock_value_difference,
            sle.item_code.as_("name"),
            sle.voucher_no,
            sle.stock_value,
            sle.batch_no,
            sle.stock_uom,
        )
        .join(se)
        .on(se.name == sle.voucher_no)
        .where(
            (sle.docstatus < 2)  # Ensure document is not cancelled
            & (sle.is_cancelled == 0)  # Ensure stock ledger entry is not cancelled
            & (se.purpose == "Manufacture")  # Include only entries with purpose "Manufacture"
        )
        .orderby(CombineDatetime(sle.posting_date, sle.posting_time))
        .orderby(sle.creation)
    )

    if items:
        query = query.where(sle.item_code.isin(items))

    query = apply_conditions(query, filters)
    results = query.run(as_dict=True)

    for result in results:
        if result.voucher_type == "Stock Entry" and not result.batch_no:
            result.actual_qty = abs(result.actual_qty)
    return results


def apply_conditions(query, filters):
    sle = frappe.qb.DocType("Stock Ledger Entry")
    warehouse_table = frappe.qb.DocType("Warehouse")

    if not filters.get("company"):
        frappe.throw(_("'Company' is required"))

    if not filters.get("from_date"):
        frappe.throw(_("'From Date' is required"))

    if not filters.get("to_date"):
        frappe.throw(_("'To Date' is required"))

    query = query.where(
        (sle.company == filters.company)
        & (sle.posting_date >= filters.from_date)
        & (sle.posting_date <= filters.to_date)
    )

    if warehouse := filters.get("warehouse"):
        if wh_conditions := apply_warehouse_filter(warehouse_table, warehouse):
            query = query.where(wh_conditions)

    if batch_no := filters.get("batch_no"):
        query = query.where(sle.batch_no == batch_no)

    if item_group := filters.get("item_group"):
        descendants = get_descendants_of("Item Group", item_group, ignore_permissions=True)
        query = query.where(sle.item_group.isin([*descendants, item_group]))

    return query


def get_item_details(items, sle):
    if not items:
        return {}
    item_details = frappe.get_all(
        "Item",
        fields=[
            "name",
            "item_name",
            "description",
            "item_group",
            "brand",
            "stock_uom",
        ],
        filters={"name": ["in", items]},
        order_by=None,
    )
    return {d.name: d for d in item_details}
