import frappe


def execute():
    shipping_tracker_items = frappe.db.get_all(
        'Shipping Tracker Item',
        fields=['name', 'parent', 'actual_arrival_date']
    )

    for item in shipping_tracker_items:
        shipping_tracker_doc = frappe.get_doc('Shipping Tracker', item.parent)
        if not item.actual_arrival_date:
            purchase_receipt_items = frappe.get_all(
                "Purchase Receipt Item",
                filters={"purchase_order": shipping_tracker_doc.purchase_order},
                fields=["parent"]
            )

            for receipt_item in purchase_receipt_items:
                purchase_receipt_doc = frappe.get_doc("Purchase Receipt", receipt_item.parent)

                if purchase_receipt_doc.posting_date:
                    frappe.db.set_value(
                        "Shipping Tracker Item",
                        item.name,
                        "actual_arrival_date",
                        purchase_receipt_doc.posting_date
                    )
                    frappe.errprint(f"Updated actual arrival date for {item.name} to {purchase_receipt_doc.posting_date}")

            frappe.db.commit()
            frappe.errprint("Actual arrival dates have been updated where applicable.")
