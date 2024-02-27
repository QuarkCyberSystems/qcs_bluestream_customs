// Copyright (c) 2024, QCS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sampling Work Order", {
	
    company: function(frm) {
        frm.set_query("cost_center", () => {
			return {
				filters: {
					"company": frm.doc.company,
				}
			};
        })
    },
	setup: function(frm) {
		frm.custom_make_buttons = {
			'Stock Entry': 'Start',
			'Pick List': 'Create Pick List',
			'Job Card': 'Create Job Card'
		};

		// Set query for warehouses
		frm.set_query("wip_warehouse", function() {
			return {
				filters: {
					'company': frm.doc.company,
				}
			};
		});

		frm.set_query("source_warehouse", function() {
			return {
				filters: {
					'company': frm.doc.company,
				}
			};
		});



		frm.set_query("sales_order", function() {
			return {
				filters: {
					"status": ["not in", ["Closed", "On Hold"]]
				}
			};
		});

		frm.set_query("fg_warehouse", function() {
			return {
				filters: {
					'company': frm.doc.company,
					'is_group': 0
				}
			};
		});

		frm.set_query("scrap_warehouse", function() {
			return {
				filters: {
					'company': frm.doc.company,
					'is_group': 0
				}
			};
		});

		// Set query for FG Item
		frm.set_query("production_item", function() {
			return {
				query: "erpnext.controllers.queries.item_query",
				filters: {
					"is_stock_item": 1,
				}
			};
		});


		// formatter for work order operation
		frm.set_indicator_formatter('operation',
			function(doc) { return (frm.doc.qty==doc.completed_qty) ? "green" : "orange"; });
	},

	onload: function(frm) {
		if (!frm.doc.status)
			frm.doc.status = 'Draft';


	},

	source_warehouse: function(frm) {
		let transaction_controller = new erpnext.TransactionController();
		transaction_controller.autofill_warehouse(frm.doc.required_items, "source_warehouse", frm.doc.source_warehouse);
	},

	refresh: function(frm) {
		erpnext.toggle_naming_series();
		erpnext.work_order.set_custom_buttons(frm);

	   
	
  
			frm.add_custom_button(__('Job Card'), function() {
				frappe.model.open_mapped_doc({
					method: "qcs_bluestream_customs.qcs_bluestream_customs.doctype.sampling_work_order.sampling_work_order.create_jc",
					frm: cur_frm,
				})
			}, __('Create'));
	
		


		
	},


	create_stock_return_entry: function(frm) {
		frappe.call({
			method: "erpnext.manufacturing.doctype.work_order.work_order.make_stock_return_entry",
			args: {
				"work_order": frm.doc.name,
			},
			callback: function(r) {
				if(!r.exc) {
					let doc = frappe.model.sync(r.message);
					frappe.set_route("Form", doc[0].doctype, doc[0].name);
				}
			}
		});
	},




	before_submit: function(frm) {
		//frm.fields_dict.required_items.grid.toggle_reqd("source_warehouse", true);
		frm.toggle_reqd("transfer_material_against",
			frm.doc.operations && frm.doc.operations.length > 0);
		frm.fields_dict.operations.grid.toggle_reqd("workstation", frm.doc.operations);
	},

	set_sales_order: function(frm) {
		if(frm.doc.production_item) {
			frappe.call({
				method: "erpnext.manufacturing.doctype.work_order.work_order.query_sales_order",
				args: { production_item: frm.doc.production_item },
				callback: function(r) {
					frm.set_query("sales_order", function() {
						erpnext.in_production_item_onchange = true;
						return {
							filters: [
								["Sales Order","name", "in", r.message]
							]
						};
					});
				}
			});
		}
	},


});

frappe.ui.form.on("Work Order Item", {
	source_warehouse: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if(!row.item_code) {
			frappe.throw(__("Please set the Item Code first"));
		} else if(row.source_warehouse) {
			frappe.call({
				"method": "erpnext.stock.utils.get_latest_stock_qty",
				args: {
					item_code: row.item_code,
					warehouse: row.source_warehouse
				},
				callback: function (r) {
					frappe.model.set_value(row.doctype, row.name,
						"available_qty_at_source_warehouse", r.message);
				}
			});
		}
	},

	item_code: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];

		if (row.item_code) {
			frappe.call({
				method: "erpnext.stock.doctype.item.item.get_item_details",
				args: {
					item_code: row.item_code,
					company: frm.doc.company
				},
				callback: function(r) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, {
							"required_qty": 1,
							"item_name": r.message.item_name,
							"description": r.message.description,
							"source_warehouse": r.message.default_warehouse,
							"allow_alternative_item": r.message.allow_alternative_item,
							"include_item_in_manufacturing": r.message.include_item_in_manufacturing
						});
					}
				}
			});
		}
	}
});

frappe.ui.form.on("Work Order Operation", {
	workstation: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if (d.workstation) {
			frappe.call({
				"method": "frappe.client.get",
				args: {
					doctype: "Workstation",
					name: d.workstation
				},
				callback: function (data) {
					frappe.model.set_value(d.doctype, d.name, "hour_rate", data.message.hour_rate);
					erpnext.work_order.calculate_cost(frm.doc);
					erpnext.work_order.calculate_total_cost(frm);
				}
			});
		}
	},
	time_in_mins: function(frm, cdt, cdn) {
		erpnext.work_order.calculate_cost(frm.doc);
		erpnext.work_order.calculate_total_cost(frm);
	},
});

erpnext.work_order = {
	set_custom_buttons: function(frm) {
		var doc = frm.doc;

		if (doc.status !== "Closed") {
			frm.add_custom_button(__('Close'), function() {
				frappe.confirm(__("Once the Work Order is Closed. It can't be resumed."),
					() => {
						erpnext.work_order.change_work_order_status(frm, "Closed");
					}
				);
			}, __("Status"));
		}

		if (doc.docstatus === 1 && !in_list(["Closed", "Completed"], doc.status)) {
			if (doc.status != 'Stopped' && doc.status != 'Completed') {
				frm.add_custom_button(__('Stop'), function() {
					erpnext.work_order.change_work_order_status(frm, "Stopped");
				}, __("Status"));
			} else if (doc.status == 'Stopped') {
				frm.add_custom_button(__('Re-open'), function() {
					erpnext.work_order.change_work_order_status(frm, "Resumed");
				}, __("Status"));
			}

			const show_start_btn = (frm.doc.skip_transfer
				|| frm.doc.transfer_material_against == 'Job Card') ? 0 : 1;

			if (show_start_btn) {
				let pending_to_transfer = frm.doc.required_items.some(
					item => flt(item.transferred_qty) < flt(item.required_qty)
				);
				if (pending_to_transfer && frm.doc.status != 'Stopped') {
					frm.has_start_btn = true;
					frm.add_custom_button(__('Create Pick List'), function() {
						erpnext.work_order.create_pick_list(frm);
					});
					var start_btn = frm.add_custom_button(__('Start'), function() {
						erpnext.work_order.make_se(frm, 'Material Transfer for Manufacture');
					});
					start_btn.addClass('btn-primary');
				}
			}

			if(!frm.doc.skip_transfer){
				// If "Material Consumption is check in Manufacturing Settings, allow Material Consumption
				if (flt(doc.material_transferred_for_manufacturing) > 0 && frm.doc.status != 'Stopped') {
					if ((flt(doc.produced_qty) < flt(doc.material_transferred_for_manufacturing))) {
						frm.has_finish_btn = true;

						if (frm.doc.__onload && frm.doc.__onload.material_consumption == 1) {
							// Only show "Material Consumption" when required_qty > consumed_qty
							var counter = 0;
							var tbl = frm.doc.required_items || [];
							var tbl_lenght = tbl.length;
							for (var i = 0, len = tbl_lenght; i < len; i++) {
								let wo_item_qty = frm.doc.required_items[i].transferred_qty || frm.doc.required_items[i].required_qty;
								if (flt(wo_item_qty) > flt(frm.doc.required_items[i].consumed_qty)) {
									counter += 1;
								}
							}
							if (counter > 0) {
								var consumption_btn = frm.add_custom_button(__('Material Consumption'), function() {
									const backflush_raw_materials_based_on = frm.doc.__onload.backflush_raw_materials_based_on;
									erpnext.work_order.make_consumption_se(frm, backflush_raw_materials_based_on);
								});
								consumption_btn.addClass('btn-primary');
							}
						}

						var finish_btn = frm.add_custom_button(__('Finish'), function() {
							erpnext.work_order.make_se(frm, 'Manufacture');
						});

						if(doc.material_transferred_for_manufacturing>=doc.qty) {
							// all materials transferred for manufacturing, make this primary
							finish_btn.addClass('btn-primary');
						}
					} else {
						frappe.db.get_doc("Manufacturing Settings").then((doc) => {
							let allowance_percentage = doc.overproduction_percentage_for_work_order;

							if (allowance_percentage > 0) {
								let allowed_qty = frm.doc.qty + ((allowance_percentage / 100) * frm.doc.qty);

								if ((flt(doc.produced_qty) < allowed_qty)) {
									frm.add_custom_button(__('Finish'), function() {
										erpnext.work_order.make_se(frm, 'Manufacture');
									});
								}
							}
						});
					}
				}
			} else {
				if ((flt(doc.produced_qty) < flt(doc.qty)) && frm.doc.status != 'Stopped') {
					var finish_btn = frm.add_custom_button(__('Finish'), function() {
						erpnext.work_order.make_se(frm, 'Manufacture');
					});
					finish_btn.addClass('btn-primary');
				}
			}
		}

	},
	calculate_cost: function(doc) {
		if (doc.operations){
			var op = doc.operations;
			doc.planned_operating_cost = 0.0;
			for(var i=0;i<op.length;i++) {
				var planned_operating_cost = flt(flt(op[i].hour_rate) * flt(op[i].time_in_mins) / 60, 2);
				frappe.model.set_value('Work Order Operation', op[i].name,
					"planned_operating_cost", planned_operating_cost);
				doc.planned_operating_cost += planned_operating_cost;
			}
			refresh_field('planned_operating_cost');
		}
	},



	set_default_warehouse: function(frm) {
		if (!(frm.doc.wip_warehouse || frm.doc.fg_warehouse)) {
			frappe.call({
				method: "erpnext.manufacturing.doctype.work_order.work_order.get_default_warehouse",
				callback: function(r) {
					if (!r.exe) {
						frm.set_value("wip_warehouse", r.message.wip_warehouse);
						frm.set_value("fg_warehouse", r.message.fg_warehouse);
						frm.set_value("scrap_warehouse", r.message.scrap_warehouse);
					}
				}
			});
		}
	},


	make_se: function(frm, purpose) {
		this.show_prompt_for_qty_input(frm, purpose)
			.then(data => {
				return frappe.xcall('erpnext.manufacturing.doctype.work_order.work_order.make_stock_entry', {
					'work_order_id': frm.doc.name,
					'purpose': purpose,
					'qty': data.qty
				});
			}).then(stock_entry => {
				frappe.model.sync(stock_entry);
				frappe.set_route('Form', stock_entry.doctype, stock_entry.name);
			});

	},


	make_consumption_se: function(frm, backflush_raw_materials_based_on) {
		if(!frm.doc.skip_transfer){
			var max = (backflush_raw_materials_based_on === "Material Transferred for Manufacture") ?
				flt(frm.doc.material_transferred_for_manufacturing) - flt(frm.doc.produced_qty) :
				flt(frm.doc.qty) - flt(frm.doc.produced_qty);
				// flt(frm.doc.qty) - flt(frm.doc.material_transferred_for_manufacturing);
		} else {
			var max = flt(frm.doc.qty) - flt(frm.doc.produced_qty);
		}

		frappe.call({
			method:"erpnext.manufacturing.doctype.work_order.work_order.make_stock_entry",
			args: {
				"work_order_id": frm.doc.name,
				"purpose": "Material Consumption for Manufacture",
				"qty": max
			},
			callback: function(r) {
				var doclist = frappe.model.sync(r.message);
				frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
			}
		});
	},


};
