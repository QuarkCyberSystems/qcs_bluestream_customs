import frappe


def execute():
    bom_list = frappe.db.get_all('BOM',
                    filters={
                        'docstatus': 1,
                        'transfer_material_against': 'Work Order'
                    },
                    fields=['name', 'item']
                )
    for bom in bom_list:
        frappe.db.set_value('BOM', bom.name, 'transfer_material_against', 'Job Card', update_modified=False)
