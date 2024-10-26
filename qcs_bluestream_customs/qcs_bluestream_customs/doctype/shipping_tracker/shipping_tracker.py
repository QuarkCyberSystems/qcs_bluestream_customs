# Copyright (c) 2024, QCS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ShippingTracker(Document):
    def after_insert(self):
        for item in self.items:
            purchase_receipt_items = frappe.get_all("Purchase Receipt Item", filters={"purchase_order": item.purchase_order}, fields=["parent"])
            for po_item in purchase_receipt_items:
                purchase_receipt_doc = frappe.get_doc("Purchase Receipt", po_item.parent)
                item.actual_arrival_date = purchase_receipt_doc.posting_date
        
        self.save()
