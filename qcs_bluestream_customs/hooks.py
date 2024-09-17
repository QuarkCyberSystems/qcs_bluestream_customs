app_name = "qcs_bluestream_customs"
app_title = "Qcs Bluestream Customs"
app_publisher = "QCS"
app_description = "Custom Code by QCS"
app_email = "support@quarkcs.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/qcs_bluestream_customs/css/qcs_bluestream_customs.css"
# app_include_js = "/assets/qcs_bluestream_customs/js/qcs_bluestream_customs.js"

# include js, css files in header of web template
# web_include_css = "/assets/qcs_bluestream_customs/css/qcs_bluestream_customs.css"
# web_include_js = "/assets/qcs_bluestream_customs/js/qcs_bluestream_customs.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "qcs_bluestream_customs/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views

doctype_js = {
	"Work Order": "public/work_order.js",
	"Pick List": "public/pick_list.js",
	"Material Request": "public/material_request.js",
	"Production Plan": "public/production_plan.js",
	"Quality Inspection": "public/quality_inspection.js",
	"Purchase Order": "public/purchase_order.js"
}

doctype_list_js = {"Job Card": "public/job_card_custom_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "qcs_bluestream_customs.utils.jinja_methods",
#	"filters": "qcs_bluestream_customs.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "qcs_bluestream_customs.install.before_install"
# after_install = "qcs_bluestream_customs.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "qcs_bluestream_customs.uninstall.before_uninstall"
# after_uninstall = "qcs_bluestream_customs.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "qcs_bluestream_customs.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Stock Entry": "qcs_bluestream_customs.override.stock_entry.BSStockEntry",
	"Job Card": "qcs_bluestream_customs.override.job_card.BSJobCard",
	"Pick List": "qcs_bluestream_customs.override.pick_list.BSPickList"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Quality Inspection": {
		"validate": "qcs_bluestream_customs.controller.quality_inspection.update_custom_quality_inspection_details"
	},
	"Purchase Receipt": {
		"on_submit": "qcs_bluestream_customs.controller.purchase_controller.update_shipping_tracker"
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "cron": {
        "* * * * *": [  
            "qcs_bluestream_customs.controller.job_card_automation.pause_and_resume_job_cards_based_on_shift",
            "qcs_bluestream_customs.controller.job_card_automation.pause_and_resume_job_cards"
        ],
       
    }
#	"all": [
#		"qcs_bluestream_customs.tasks.all"
#	],
#	"daily": [
#		"qcs_bluestream_customs.tasks.daily"
#	],
#	"hourly": [
#		"qcs_bluestream_customs.tasks.hourly"
#	],
#	"weekly": [
#		"qcs_bluestream_customs.tasks.weekly"
#	],
#	"monthly": [
#		"qcs_bluestream_customs.tasks.monthly"
#	],
}

fixtures = [
	{
		"dt": "Property Setter", "filters": [
			[
				"name", "in", [
					'Work Order-status-in_list_view',
					'Stock Entry-custom_sampling_work_order',
					'Job Card-custom_sampling_work_order',
					'Production Plan-transfer_materials-hidden'
					'Quality Inspection-reference_type-reqd',
					'Quality Inspection-reference_name-reqd',
					'Quality Inspection-main-field_order',
					'Quality Inspection-status-options',
					'Non Conformance-main-naming_rule',
					'Non Conformance-main-autoname',
					'Non Conformance-details-label',
					'Non Conformance-main-field_order',
				]
			]
		]
	},
	{
		"dt": "Custom Field", "filters": [
			[
				"name", "in", [
					'Production Plan-custom_row_materials_for_purchase',
					'Production Plan-custom_purchase_warehouse',
					'Pick List-custom_job_card',
					'Pick List Item-custom_job_card_item',
					'Material Request-custom_sales_order'
				]
			]
		],
	},
]

# Testing
# -------

# before_tests = "qcs_bluestream_customs.install.before_tests"
# Overriding Methods
# ------------------------------

override_whitelisted_methods = {
	"erpnext.stock.doctype.pick_list.pick_list.create_stock_entry": "qcs_bluestream_customs.controller.pick_list.create_stock_entry"
}

# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "qcs_bluestream_customs.task.get_dashboard_data"
# }
override_doctype_dashboards = {
	"Purchase Order": "qcs_bluestream_customs.controller.purchase_order_dashboard.get_dashboard_for_purchase_order" 
}


# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]


# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"qcs_bluestream_customs.auth.validate"
# ]
