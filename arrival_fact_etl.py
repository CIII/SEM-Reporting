"""Arrival fact table etl"""

__copyright__ = "Copyright (C) 2016 TapQuality"
__docformat__ = "restructuredtext"

import mysql.connector
import progressbar
import argparse
import subprocess
import json
import warehouse as _w
from googleads import adwords
from datetime import datetime

easiersolar = mysql.connector.connect(option_files='easiersolardb.cnf')
sitebrain = mysql.connector.connect(option_files='sitebraindb.cnf')
leadpath = mysql.connector.connect(option_files='leadpathdb.cnf')
tq_reporting = mysql.connector.connect(option_files='tqreportingdb.cnf')
easiersolar2 = mysql.connector.connect(option_files='easiersolardb.cnf')

import logging
#for debugging change this to WARN
logging.basicConfig(filename='arrival_facts_etl.log',level=logging.ERROR)

default_high_water_mark = '2016-01-01 00:00:00'
time_now_query = 'select now()'
parser = argparse.ArgumentParser()
parser.add_argument("--start-date", help="forced high-water-mark/processing start date")
parser.add_argument('--update-adwords', dest='update_adwords', action='store_true')
parser.add_argument('--dont-update-adwords', dest='update_adwords', action='store_false')
parser.set_defaults(update_adwords=True)
args = parser.parse_args()

try:
	#check max time in fact table
	#create timestamp window from then minus [window-repeat] thru now
	#TODO: implement window-repeat
	sb_cursor = sitebrain.cursor()
	lp_cursor = leadpath.cursor()
	es_cursor2 = easiersolar2.cursor()
	tqr_cursor = tq_reporting.cursor()

	if args.start_date is None:
		tqr_cursor.execute("select max(updated_at) from %s" % _w.arrival_facts.name)
		high_water_mark = tqr_cursor.fetchall()
		high_water_mark = high_water_mark[0][0]
		if not high_water_mark:
			print 'high water mark not found, using %s' % default_high_water_mark
			high_water_mark = default_high_water_mark
		else:
			high_water_mark = high_water_mark.isoformat()
	else:
		high_water_mark = args.start_date

	tqr_cursor.execute(time_now_query)
	time_now = tqr_cursor.fetchall()
	time_now = time_now[0][0].isoformat()

	#############
	# starting with easiersolar db
	query_sql = '''
		select
			arrivals.id,  -- internal joining id
			arrivals.arrival_id,  -- external/global identifier
			arrivals.created_at,
			arrivals.updated_at,
			user_agent,
			ip,
			gclid
		from
			arrivals
		join
			browsers on arrivals.browser_id = browsers.id
		where
			arrivals.created_at > '{high_water_mark}'
			and arrivals.created_at <= '{time_now}'
	'''.format(**locals())

	#TODO: recalculate high water mark based on all dependant table updates
	#TODO: ^rather, maybe run a cron job that sets given arrivals to updates if one
	# of their dependant tables is updated

	es_cursor = easiersolar.cursor(buffered=True)
	es_cursor.execute(query_sql)

	rows = es_cursor.fetchall()
	print '%d arrivals found for given timeframe' % len(rows)

	#for each row in easiersolar arrivals db
	for index, row in enumerate(rows):
		progressbar.printProgress(index, len(rows), prefix = 'Progress:', suffix = 'Complete', barLength = 25)
		_w.arrival_facts.clear_data()

		#####################
		#get data from current easiersolar arrival row
		row = list(row)
		arrival_id_internal = row[0]
		arrival_id_external = row[1]
		_w.created_at.data = row[2]
		_w.updated_at.data = row[3]
		_w.user_agent.data = row[4]
		_w.ip_address.data = row[5]
		_w.gclid.data = row[6]
		if _w.gclid.data:
			_w.has_gclid.data = 1
		else:
			_w.has_gclid.data = 0
			_w.gclid.data = None #incase of the blank string case
		_w.day_of_week.data = _w.created_at.data.strftime('%A')


		#########################
		#parse user agent
		cmd="ruby user_agent_parser.rb \"%s\"" % _w.user_agent.data
		p=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
		(output, errors) = p.communicate()

		user_agent_data = json.loads(output)

		_w.browser.data = user_agent_data[1]
		_w.browser_version.data = user_agent_data[2]
		_w.os_name.data = user_agent_data[3]
		_w.os_version.data = user_agent_data[4]
		##################
		is_bot = user_agent_data[5]
		bot_name = user_agent_data[6]
		##################
		_w.device_name.data = user_agent_data[7]
		_w.device_type.data = user_agent_data[8]
		_w.device_brand.data = user_agent_data[9]
		#if is bot, skip this row
		if is_bot:
			continue
		#sanitize data
		if(_w.device_name.data is not None):
			_w.device_name.data = _w.device_name.data.replace("'", "-")

		if isinstance(_w.user_agent.data, basestring):
			if 'ruxit' in _w.user_agent.data or 'Ruxit' in _w.user_agent.data:
				continue


		######################
		#easiersolar events
		event_sql = '''
			select
				count(*)
			from
				events
			where
				arrival_id = %s
		''' % arrival_id_internal

		es_cursor2.execute(event_sql)
		_w.events.data = es_cursor2.fetchall()[0][0]

		#assume cold-feet, if not adjust
		_w.event_category.data = 'cold-feet'
		_w.coldfeet.data = 1
		_w.dropoff.data = 0
		if _w.events.data < 2:
			_w.event_category.data = 'dropoff'
			_w.coldfeet.data = 0
			_w.dropoff.data = 1

		#cone = converting event
		cone_sql = '''
			select
				*
			from
				events join
				event_types 
					on events.event_type_id=event_types.id
			where 
				arrival_id = %s and
				event_types.name='Form Complete';
		''' % arrival_id_internal

		es_cursor2.execute(cone_sql)
		cone = es_cursor2.fetchall()
		if cone and cone[0][0]:
			_w.event_category.data = 'converted'
			_w.converted.data = 1
			_w.coldfeet.data = 0
			_w.dropoff.data = 0
		else:
			_w.converted.data = 0


		##############
		# easiersolar forms
		form_sql = '''
			select 
				city, state, zip, property_ownership
			from
				forms
			where
				arrival_id = %s
		''' % arrival_id_internal
		es_cursor2.execute(form_sql)
		conf = es_cursor2.fetchall()
		if conf and conf[0]:
			_w.form_city.data = conf[0][0]
			_w.form_state.data = conf[0][1]
			_w.form_zip.data = conf[0][2]
			_w.prop_own.data = conf[0][3]
			_w.conf.data = 1
		else:
			_w.conf.data = 0
			_w.form_city.data = None
			_w.form_state.data = None
			_w.form_zip.data = None
			_w.prop_own.data = None


		###############
		# sitebrain db 90_arrival data
		sb_sql = '''
			select
				top_level_domain,
				a.utm_value as source,
				b.utm_value as medium,
				c.utm_value as term,
				d.utm_value as content,
				e.utm_value as campaign
			from
				90_arrivals
				left join 90_arrival_utm_parameters on
					90_arrivals.id = 90_arrival_utm_parameters.arrival_id
				left join utm_values a on
					a.id = 90_arrival_utm_parameters.utm_source_id
				left join utm_values b on
					b.id = 90_arrival_utm_parameters.utm_medium_id
				left join utm_values c on
					c.id = 90_arrival_utm_parameters.utm_term_id
				left join utm_values d on
					d.id = 90_arrival_utm_parameters.utm_content_id
				left join utm_values e on
					e.id = 90_arrival_utm_parameters.utm_campaign_id
				left join browsers on
					browser_id = browsers.id
				left join referrer_domains on
					referrer_domains.id = referrer_domain_id
			where
				90_arrivals.external_id = '{arrival_id_external}'
		'''.format(**locals())

		sb_cursor.execute(sb_sql)
		sb_data = sb_cursor.fetchall()
		if sb_data and sb_data[0]:
			_w.sitebrain_connected.data = 1
			_w.top_level_domain.data = sb_data[0][0]
			_w.source.data = sb_data[0][1]
			_w.medium.data = sb_data[0][2]
			_w.term.data = sb_data[0][3]
			_w.content.data = sb_data[0][4]
			_w.campaign.data = sb_data[0][5]
		else:
			_w.sitebrain_connected.data = 0
			_w.top_level_domain.data = None
			_w.source.data = None
			_w.medium.data = None
			_w.term.data = None
			_w.content.data = None
			_w.campaign.data = None


		#####################
		#sitebrain ab test data thru pixelfires
		sb_sql = '''
			select
				t.name,
				tv.name,
				abv.redirect_url,
				pf.url,
				sum(pf.revenue)
			from
				90_arrivals ar
				left join 90_pixel_fires pf
					on pf.arrival_id = ar.id
				left join 90_pixel_fire_ab_test_variations pfabv
					on pf.id = pfabv.pixel_fire_id
				left join pixel_ab_test_variations abv
					on pfabv.pixel_ab_test_variation_id = abv.id
				left join test_variations tv
					on abv.test_variation_id = tv.id
				left join tests t
					on tv.test_id = t.id
			where
				ar.external_id = '{arrival_id_external}'
			group by ar.external_id
		'''.format(**locals())

		sb_cursor.execute(sb_sql)
		sb_data = sb_cursor.fetchall()
		if sb_data and sb_data[0]:
			_w.ab_test.data = sb_data[0][0]
			_w.ab_variation.data = sb_data[0][1]
			_w.ab_variation_url.data = sb_data[0][2]
			_w.dest_url.data = sb_data[0][3]
			_w.revenue_sb.data = sb_data[0][4]
		else:
			_w.ab_test.data = None
			_w.ab_variation.data = None
			_w.ab_variation_url.data = None
			_w.dest_url.data = None
			_w.revenue_sb.data = 0


		###############
		# leadpath data
		lp_sql = '''
			select
				sum(lead_matches.price),
				max(lead_matches.updated_at)
			from
				arrivals
				join leads on
					arrivals.id = leads.arrival_id
				left join lead_matches on
					lead_matches.lead_id = leads.id
			where
				arrivals.external_id = '{arrival_id_external}'
				and lead_matches.status = 4
			group by
				arrivals.external_id
		'''.format(**locals())
		lp_cursor.execute(lp_sql)
		lp_data = lp_cursor.fetchall()
		if lp_data and lp_data[0]:
			_w.revenue_lp.data = lp_data[0][0]
			conversion_time = lp_data[0][1]
		else:
			_w.revenue_lp.data = 0
			conversion_time = None


		##############
		#adwords upload and we have valid conversion time
		if(args.update_adwords and conversion_time is not None and _w.created_at.data is not None):
			#adwords only allows a 90 day range
			if((datetime.now() - conversion_time).days < 90 and (datetime.now() - _w.created_at.data).days < 90):
				if(_w.gclid.data and _w.revenue_lp.data > 0):
					client = adwords.AdWordsClient.LoadFromStorage()
					offline_conversion_feed_service = client.GetService('OfflineConversionFeedService', version='v201609')
					feed = {
						'conversionName': 'TQLeadsImport',
						'conversionTime': datetime.strftime(conversion_time, "%Y%m%d %H%M%S Etc/GMT"), #note gmt ~= utc
						'conversionValue': _w.revenue_lp.data,
						'googleClickId': _w.gclid.data,
					}
					offline_conversion_operation = {
						'operator': 'ADD',
						'operand': feed
					}

					try:
						offline_conversion_response = offline_conversion_feed_service.mutate([offline_conversion_operation])
						return_vals = offline_conversion_response['value'][0]
						logging.warn(return_vals) #this is warn level for debugging. if this is info it gets drowned out in a huge amout of info log messages from the google package
					except Exception as err:
						logging.error("adwords upload error for arrival %s: ``%s``" % (arrival_id_external, err.message))


		################
		# ip blacklisting
		ip_bl_sql = '''
				select distinct ip
				from ip_blacklist
				where ip is not NULL
		'''
		#assume not on blacklist; else update
		_w.is_ip_blacklisted.data = 0
		_w.ip_blacklisted.data = 0
		tqr_cursor.execute(ip_bl_sql)
		ip_bl_data = tqr_cursor.fetchall()
		if _w.ip_address.data:
			if ip_bl_data and ip_bl_data[0]:
				ip_list = map(lambda x: x[0], ip_bl_data)
				if(_w.ip_address.data in ip_list):
					_w.is_ip_blacklisted.data = 1
					_w.ip_blacklisted.data = 1
			else:
				logging.warn("ip blacklist error")
		else:
			# row's ip address invalid or null
			pass


		##################
		# row done; cleanup and insert into fact table
		_w.arrival_id.data = arrival_id_external
		if _w.revenue_sb.data is None:
			_w.revenue_sb.data = 0
		if _w.revenue_lp.data is None:
			_w.revenue_lp.data = 0

		tqr_cursor.execute(_w.arrival_facts.insert_data())
		tq_reporting.commit()

	print '\nDone.'


finally:
	easiersolar.close()
	tq_reporting.close()
	sitebrain.close()
	leadpath.close()
	easiersolar2.close()

