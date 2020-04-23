"""Warehouse"""

__copyright__ = "Copyright (C) 2016 TapQuality"
__docformat__ = "restructuredtext"

from warehouse_classes import Field, FactTable

#define fields
#dimensions
arrival_id = Field("arrival_id", "varchar(255)")
created_at = Field("created_at", "timestamp")
updated_at = Field("updated_at", "timestamp")
event_category = Field("event_category", "varchar(9)")
form_city = Field("form_city", "varchar(50)")
form_state = Field("form_state", "varchar(12)")
form_zip = Field("form_zip", "varchar(12)")
prop_own = Field("prop_own", "varchar(12)")
top_level_domain = Field("top_level_domain", "varchar(255)")
user_agent = Field("user_agent", "varchar(255)")
browser = Field("browser", "varchar(50)")
browser_version = Field("browser_version", "varchar(50)")
device_type = Field("device_type", "varchar(50)")
source = Field("source", "varchar(64)")
medium = Field("medium", "varchar(64)")
term = Field("term", "varchar(64)")
content = Field("content", "varchar(64)")
campaign = Field("campaign", "varchar(64)")
day_of_week = Field("day_of_week", "varchar(50)")
os_name = Field("os_name", "varchar(64)")
os_version = Field("os_version", "varchar(64)")
device_name = Field("device_name", "varchar(64)")
device_brand = Field("device_brand", "varchar(64)")
ip_address = Field("ip_address", "varchar(20)")
ab_test = Field("ab_test", "varchar(100)")
ab_variation = Field("ab_variation", "varchar(100)")
ab_variation_url = Field("ab_variation_url", "varchar(255)")
dest_url = Field("dest_url", "varchar(255)")
gclid = Field("gclid", "varchar(255)")
is_ip_blacklisted = Field("is_ip_blacklisted", "tinyint(1)", True)

#measures
events = Field("events", "int(8)", True)
converted = Field("converted", "tinyint(1)", True)
coldfeet = Field("coldfeet", "tinyint(1)", True)
dropoff = Field("dropoff", "tinyint(1)", True)
conf = Field("conf", "tinyint(1)", True)
sitebrain_connected = Field("sitebrain_connected", "tinyint(1)", True)
has_gclid = Field("has_gclid", "tinyint(1)", True)
revenue_sb = Field("revenue_sb", "decimal(6,2)", True)
revenue_lp = Field("revenue_lp", "decimal(6,2)", True)
ip_blacklisted = Field("ip_blacklisted", "tinyint(1)", True)

#define fact tables

#arrival facts
arrival_facts_dimensions = [
	arrival_id,
	created_at,
	updated_at,
	event_category,
	form_city,
	form_state,
	form_zip,
	prop_own,
	top_level_domain,
	user_agent,
	browser,
	browser_version,
	device_type,
	source,
	medium,
	term,
	content,
	campaign,
	day_of_week,
	os_name,
	os_version,
	device_name,
	device_brand,
	ip_address,
	ab_test,
	ab_variation,
	ab_variation_url,
	dest_url,
	gclid,
	is_ip_blacklisted,
]
arrival_facts_measures = [
	events,
	converted,
	coldfeet,
	dropoff,
	conf,
	sitebrain_connected,
	has_gclid,
	revenue_sb,
	revenue_lp,
	ip_blacklisted,
]

#sitebrain arrival facts
sb_arrival_facts_dimensions = [
	arrival_id,
	created_at,
	updated_at,
]
sb_arrival_facts_measures = [
	#tq_connected,
	events,
]

arrival_facts = FactTable("arrival_facts_staging", arrival_facts_dimensions, arrival_facts_measures)

sb_arrival_facts = FactTable("sb_arrival_facts_staging", sb_arrival_facts_dimensions, sb_arrival_facts_measures)
