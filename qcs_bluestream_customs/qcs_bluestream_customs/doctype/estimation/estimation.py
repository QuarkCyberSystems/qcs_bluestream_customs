# Copyright (c) 2024, QCS and contributors
# For license information, please see license.txt

import frappe
import datetime

from frappe.model.document import Document
from frappe.utils import add_days, getdate, today


class Estimation(Document):
    def after_insert(self):
        estimation_id = self.name
        quotation_id = self.quotation
        frappe.db.set_value('Quotation', quotation_id, 'estimation', estimation_id)

    def on_submit(self):
        estimation_id = self.name
        quotation_id = self.quotation
        opportunity_id = self.opportunity
        frappe.db.set_value('Quotation', quotation_id, 'quotation_status', 'Estimation Completed')
        frappe.db.set_value('Opportunity', opportunity_id, 'custom_estimation', estimation_id)


# @frappe.whitelist()
# def calculate_turn_around_time_date(row_name, days_to_add, start_date):
#     try:
#         days_to_add = int(days_to_add)
#     except ValueError:
#         frappe.throw(f"Invalid value for days_to_add: {days_to_add}")

#     start_date = getdate(start_date)

#     holiday_list = frappe.db.get_single_value("Turn Around Time Settings", "holiday_list")
#     holiday_dates = frappe.get_all("Holiday", filters={"parent": holiday_list}, fields=["holiday_date"])

#     if not holiday_list:
#         frappe.throw("Holiday List not found in Turn Around Time Settings")

#     formatted_holiday_dates = [
#         holiday['holiday_date'].strftime('%Y-%m-%d') if isinstance(holiday['holiday_date'], (datetime.date, datetime.datetime)) else holiday['holiday_date'] 
#         for holiday in holiday_dates
#     ]

#     turn_around_time_date = start_date

#     while days_to_add > 0:
#         turn_around_time_date = add_days(turn_around_time_date, 1)

#         if not is_holiday(formatted_holiday_dates, turn_around_time_date):
#             days_to_add -= 1

#     return turn_around_time_date


# def is_holiday(holiday_dates, date=None):
#     """Returns true if the given date is a holiday in the given holiday list"""
#     if date is None:
#         date = today()

#     date_str = date.strftime('%Y-%m-%d')
#     return date_str in holiday_dates
