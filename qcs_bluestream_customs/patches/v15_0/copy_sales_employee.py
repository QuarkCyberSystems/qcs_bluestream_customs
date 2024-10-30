import frappe
from frappe.utils import today


def execute():
    batch_size = 100
    last_processed_date = None

    end_date = today()

    while True:
        filters = {
            'employee': ['!=', ''],
            'transaction_date': ['<=', end_date]
        }

        if last_processed_date:
            filters['transaction_date'] = ['>', last_processed_date]

        quotations = frappe.get_all(
            'Quotation',
            filters=filters,
            fields=['name', 'employee', 'transaction_date'],
            order_by='transaction_date asc',
            limit_page_length=batch_size
        )

        if not quotations:
            break

        for quotation in quotations:
            sales_person = frappe.db.get_value(
                'Sales Person', {'employee': quotation.employee}, 'name'
            )

            if sales_person:
                frappe.db.set_value(
                    'Quotation', quotation.name, 'custom_sales_person', sales_person, update_modified=False
                )
                frappe.errprint(
                    f"Set custom_sales_person to {sales_person} for Quotation {quotation.name}"
                )
            else:
                frappe.errprint(
                    f"No Sales Person found for employee {quotation.employee} in Quotation {quotation.name}"
                )

        last_processed_date = quotations[-1]['transaction_date']
        frappe.db.commit()
