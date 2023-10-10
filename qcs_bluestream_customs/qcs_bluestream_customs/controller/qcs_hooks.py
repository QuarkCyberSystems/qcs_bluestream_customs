# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import copy
import json
from typing import Dict, List, Optional

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import (
	cint,
	cstr,
	flt,
	formatdate,
	get_link_to_form,
	getdate,
	now_datetime,
	nowtime,
	strip,
	strip_html,
)
from frappe.utils.html_utils import clean_html


def add_item_description(item, method):
    frappe.errprint("validate")
    item.description += "Test"
    if item.attributes:
        for att in item.attributes:
            item.description += "-" att.attribute + " : " + att.attribute_value