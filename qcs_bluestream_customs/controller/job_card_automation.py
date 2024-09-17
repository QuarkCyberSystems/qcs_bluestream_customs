import frappe
from datetime import datetime, timedelta
from frappe.utils import now_datetime, get_datetime, time_diff_in_seconds
from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday


def create_job_card_automation_log(job_card, remarks=None, error=None):
    if error:  # Only create log entries if there's an error
        try:
            log = frappe.get_doc({
                "doctype": "Job Card Automation Log",
                "job_card": job_card,
                "remarks": remarks or '',
                "error": error
            })
            log.insert(ignore_permissions=True)
            frappe.db.commit()  
        except Exception as e:
            frappe.log_error(f"Error while logging Job Card automation: {str(e)}", "Job Card Automation Logging Error")


def pause_and_resume_job_cards_based_on_shift():
    try:
        settings = frappe.get_single("Job Card Automation Settings")
        
        if not settings.shift:
            return

        shift = frappe.get_doc("Shift Type", settings.shift)
        if not (shift.start_time and shift.end_time):
            return
        
        if isinstance(shift.start_time, timedelta):
            start_shift_time = (datetime.min + shift.start_time).time() 
        else:
            start_shift_time = shift.start_time

        if isinstance(shift.end_time, timedelta):
            end_shift_time = (datetime.min + shift.end_time).time()
        else:
            end_shift_time = shift.end_time

        current_time = now_datetime().time()
        today_date = now_datetime().date()

        holiday_list = settings.holiday_list
        if is_holiday(holiday_list, today_date):
            return
        
        job_cards = frappe.get_all("Job Card", filters={"docstatus": 0, "status": ["in", ["Work In Progress", "On Hold"]]}, fields=["name", "status", "custom_skip_automation"])

        for job_card in job_cards:
            job_card_doc = frappe.get_doc("Job Card", job_card.name)
            if job_card_doc.get("custom_skip_automation"):
                continue

            # Resume job card if within shift time
            if start_shift_time <= current_time < end_shift_time:
                if job_card_doc.status == "On Hold":
                    job_card_doc.db_set("status", "Work In Progress")
                    
                    new_args = frappe._dict({
                        "from_time": get_datetime(now_datetime()),
                        "operation": job_card_doc.operation,
                        "completed_qty": 0.0
                    })
                    employees = job_card_doc.get("employee") or []
                    if employees:
                        for name in employees:
                            new_args.employee = name.employee
                            job_card_doc.append("time_logs", new_args)
                    else:
                        job_card_doc.append("time_logs", new_args)
                    job_card_doc.save()
                    create_job_card_automation_log(job_card_doc.name, remarks="Resumed during shift")

            if current_time >= end_shift_time:
                if job_card_doc.status == "Work In Progress":
                    job_card_doc.db_set("status", "On Hold")
                    
                    if job_card_doc.time_logs:
                        for row in job_card_doc.time_logs:
                            if not row.to_time:
                                row.to_time = get_datetime(now_datetime()).strftime('%Y-%m-%d %H:%M:%S')
                                row.time_in_mins = time_diff_in_seconds(row.to_time, row.from_time) / 60
                                row.db_set('to_time', row.to_time)
                                row.db_set('time_in_mins', row.time_in_mins)
                    job_card_doc.save()
                    create_job_card_automation_log(job_card_doc.name, remarks="Paused after shift end")

    except Exception as e:
        create_job_card_automation_log(None, "Error processing job cards based on shift.", str(e))


def pause_and_resume_job_cards():
    try:
        settings = frappe.get_single("Job Card Automation Settings")
        if settings.start_lunch_time and settings.end_lunch_time:
            start_lunch_time = datetime.strptime(settings.start_lunch_time, '%H:%M:%S').time()
            end_lunch_time = datetime.strptime(settings.end_lunch_time, '%H:%M:%S').time()
            current_time = now_datetime().time()
            today_date = now_datetime().date()
            holiday_list = settings.holiday_list

            shift = frappe.get_doc("Shift Type", settings.shift)
            end_shift_time = shift.end_time if not isinstance(shift.end_time, timedelta) else (datetime.min + shift.end_time).time()

            if current_time >= end_shift_time:
                return

            if is_holiday(holiday_list, today_date):
                return
            
            job_cards = frappe.get_all("Job Card", filters={"docstatus": 0, "status": ["in", ["Work In Progress", "On Hold"]]}, fields=["name", "status", "custom_skip_automation"])
            for job_card in job_cards:
                job_card_doc = frappe.get_doc("Job Card", job_card.name)
                if job_card_doc.get("custom_skip_automation"):
                    continue

                # Pause job card during lunch
                if start_lunch_time <= current_time <= end_lunch_time:
                    if job_card_doc.status == "Work In Progress":
                        job_card_doc.db_set("status", "On Hold")

                        if job_card_doc.time_logs:
                            for row in job_card_doc.time_logs:
                                if not row.to_time:
                                    row.to_time = get_datetime(now_datetime()).strftime('%Y-%m-%d %H:%M:%S')
                                    row.time_in_mins = time_diff_in_seconds(row.to_time, row.from_time) / 60
                                    row.db_set('to_time', row.to_time)
                                    row.db_set('time_in_mins', row.time_in_mins)
                        job_card_doc.save()
                        create_job_card_automation_log(job_card_doc.name, remarks="Paused for lunch")

                # Resume job card after lunch
                elif current_time > end_lunch_time and current_time < end_shift_time:
                    if job_card_doc.status == "On Hold":
                        job_card_doc.db_set("status", "Work In Progress")
                        
                        new_args = frappe._dict({
                            "from_time": get_datetime(now_datetime()),
                            "operation": job_card_doc.operation,
                            "completed_qty": 0.0
                        })

                        employees = job_card_doc.get("employee") or []
                        if employees:
                            for name in employees:
                                new_args.employee = name.employee
                                job_card_doc.append("time_logs", new_args)
                        else:
                            job_card_doc.append("time_logs", new_args)

                        job_card_doc.save()
                        create_job_card_automation_log(job_card_doc.name, remarks="Resumed after lunch")

        else:
            frappe.log_error("Lunch time settings are missing.", "Pause/Resume Job Card Error")
            
    except Exception as e:
        create_job_card_automation_log(None, "Error processing job cards during lunch time.", str(e))

@frappe.whitelist()
def pause_job_card(job_card_name):
    """Pause the job card and mark it as 'On Hold' if skip automation is not set."""
    try:
        job_card = frappe.get_doc("Job Card", job_card_name)
        
        if job_card.status == "Work In Progress":
            job_card.db_set("status", "On Hold")

            if job_card.time_logs:
                for row in job_card.time_logs:
                    if not row.to_time:
                        row.to_time = get_datetime(now_datetime()).strftime('%Y-%m-%d %H:%M:%S')
                        row.time_in_mins = time_diff_in_seconds(row.to_time, row.from_time) / 60
                        row.db_set('to_time', row.to_time)
                        row.db_set('time_in_mins', row.time_in_mins)
            return
        else:
            frappe.throw("Job Card is not in 'Work In Progress' state.")
    except Exception as e:
        frappe.throw(f"Error pausing job card: {str(e)}")


@frappe.whitelist()
def resume_job_card(job_card_name):
    """Resume the job card and mark it as 'Work In Progress' if skip automation is not set."""
    try:
        job_card = frappe.get_doc("Job Card", job_card_name)
        if job_card.status == "On Hold":
            job_card.db_set("status", "Work In Progress")

            new_args = frappe._dict({
                "from_time": get_datetime(now_datetime()),
                "operation": job_card.operation,
                "completed_qty": 0.0
            })
            employees = job_card.get("employee") or []
            if employees:
                for name in employees:
                    new_args.employee = name.employee
                    job_card.append("time_logs", new_args)
            else:
                job_card.append("time_logs", new_args)
            job_card.save()

            return
        else:
            frappe.throw("Job Card is not in 'On Hold' state.")
    except Exception as e:
        frappe.throw(f"Error resuming job card: {str(e)}")


@frappe.whitelist()
def set_skip_automation(job_card_name):
    """Set the skip automation field for the selected Job Cards."""
    try:
        job_card = frappe.get_doc("Job Card", job_card_name)
        job_card.custom_skip_automation = 1
        job_card.save()
    except Exception as e:
        frappe.throw(f"Error updating Job Cards: {str(e)}")
