frappe.ui.form.on('Production Plan', {
    refresh:(frm) =>{
        frm.set_query("for_warehouse", function (doc) {
			return {
				filters: {
					company: doc.company,
				},
			};
		});
		// if (frm.doc.docstatus === 1) {
		// 	if (frm.doc.po_items && frm.doc.status !== "Closed") {
		// 		frm.add_custom_button(
		// 			__("Work Orders / Subcontract PO"),
		// 			() => {
		// 				frm.trigger("make_work_orders");
		// 			},
		// 			__("Create")
		// 		);
		// 	}
		// }
    },
	
	// make_work_orders(frm) {
	// 	frappe.call({
	// 		method: "qcs_bluestream_customs.controller.production_plan.make_work_order1",
	// 		args:{
	// 			"doc": frm.doc,
	// 		},
	// 		callback: function () {
	// 			frm.reload_doc();
	// 		},
	// 	});
	// },
	get_items_for_mr(frm) {
		if (!frm.doc.for_warehouse) {
			frm.trigger("toggle_for_warehouse");
			frappe.throw(__("Select the Warehouse"));
		}

		frm.events.get_items_for_material_requests(frm, [
			{
				warehouse: frm.doc.for_warehouse,
			},
		]);
	},
	custom_purchase_warehouse(frm) {
		frm.events.get_items_for_material_requests(frm, [
			{
				warehouse: frm.doc.for_warehouse,
			},
		]);
	},
	transfer_materials(frm) {
		if (!frm.doc.for_warehouse) {
			frm.trigger("toggle_for_warehouse");
			frappe.throw(__("Select the Warehouse"));
		}

		frm.set_value("consider_minimum_order_qty", 0);

		if (frm.doc.ignore_existing_ordered_qty) {
			frm.events.get_items_for_material_requests(frm);
		} else {
			let warehouses = [{"warehouse":"All Warehouses - BSE"}]
			frm.events.get_items_for_material_requests(frm, warehouses);
		}
	},
    get_items_for_material_requests(frm, warehouses) {
		frappe.call({
			method: "qcs_bluestream_customs.controller.production_plan.get_items_for_material_requests",
			freeze: true,
			args: {
				doc: frm.doc,
				warehouses: warehouses || [],
			},
			callback: function (r) {
				if (r.message) {
					frm.set_value("mr_items", []);
					r.message.forEach((row) => {
						let d = frm.add_child("mr_items");
						for (let field in row) {
							if (field !== "name") {
								d[field] = row[field];
							}
						}
					});
				}
				refresh_field("mr_items");
			},
		});
	},
    
})