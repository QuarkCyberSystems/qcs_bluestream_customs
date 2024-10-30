import frappe


def execute():
    shipping_trackers = frappe.db.get_all(
        'Shipping Tracker', fields=['name', 'purchase_order']
    )
    for tracker in shipping_trackers:
        child_table = frappe.get_all(
            'Shipping Tracker Item', filters={'parent': tracker.name}
        )

        if not child_table:
            purchase_order_items = frappe.get_all(
                'Purchase Order Item',
                filters={'parent': tracker.purchase_order},
                fields=['item_code', 'item_name', 'description', 'qty', 'uom']
            )

            for po_item in purchase_order_items:
                child = frappe.get_doc({
                    'doctype': 'Shipping Tracker Item',
                    'parent': tracker.name,
                    'parentfield': 'items',
                    'parenttype': 'Shipping Tracker',
                    'item_code': po_item.item_code,
                    'item_name': po_item.item_name,
                    'description': po_item.description,
                    'qty': po_item.qty,
                    'uom': po_item.uom
                })
                child.insert(ignore_permissions=True)

            frappe.db.commit()
