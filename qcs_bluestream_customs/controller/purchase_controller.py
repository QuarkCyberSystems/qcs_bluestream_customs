import frappe


def update_shipping_tracker(doc, method):
    for item in doc.items:
        if item.purchase_order_item:
            shipping_tracker_items = frappe.get_all(
                "Shipping Tracker Item",
                filters={"purchase_order_item": item.purchase_order_item},
                fields=["name", "actual_arrival_date"]
            )
            for sti in shipping_tracker_items:
                shipping_tracker_item = frappe.get_doc("Shipping Tracker Item", sti.name)
                shipping_tracker_item.actual_arrival_date = doc.posting_date
                shipping_tracker_item.save()
