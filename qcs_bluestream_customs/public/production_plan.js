frappe.ui.form.on('Production Plan', {
    refresh:(frm) =>{
        frm.set_query("for_warehouse", function (doc) {
			return {
				filters: {
					company: doc.company,
				},
			};
		});
    },
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