frappe.ui.form.on("Work Order", {
	onload(frm) {
        if(cur_frm.doc.transfer_material_against == "Job Card"){
			if(cur_frm.doc.operations){
				let count = [];
				frm.doc.operations.forEach(op => {
					if (op.completed_qty === cur_frm.doc.qty) {
						count.push(1);
					}
					else{
						count.push(0);
					}
				})
				const allSameNotZero = count.every((value) => value === count[0] && value !== 0);
				if (allSameNotZero) {
					if( frm.doc.material_transferred_for_manufacturing != cur_frm.doc.qty) {
						frm.set_value("material_transferred_for_manufacturing", cur_frm.doc.qty)
						frm.save('Update');
					}
				}
			}
		}
	},
	refresh(frm) {
		if(cur_frm.doc.actual_start_date){
			if(cur_frm.doc.status != "In Process" && cur_frm.doc.status === "Not Started"){
				frm.set_value("status", "In Process")
				frm.save('Update');
			}
		}
    }
})