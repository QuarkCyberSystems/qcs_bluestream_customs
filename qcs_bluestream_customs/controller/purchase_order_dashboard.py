
from frappe import _


def get_dashboard_for_purchase_order(data):
	data["transactions"].extend(
		[
			{"label": _("Shipment"), "items": ["Shipping Tracker"]},
			
		]
	)
	return data