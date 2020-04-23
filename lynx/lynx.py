#!/usr/bin/python

import json
import subprocess
import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from termcolor import colored
import csv
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, func
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import asc, bindparam
from os.path import dirname, abspath, join
import os
from user_agents import parse

import tables

es_cnf = ''
tq_cnf = ''


# TODO CREATED AT NEED TO ADD, ADD FACT TABLE UPDATE TO DELETE
# TODO LAST ACTIVITY IN LYNX, NEED TO COMPARE, ADD TO ETL, ADD CREATED AT
def load_es_session(es_engine):
    """"""
    Session = sessionmaker(bind=es_engine)
    session = Session()
    return session


def load_tq_session(tq_engine):
    """"""
    Session = sessionmaker(bind=tq_engine)
    session = Session()
    return session


def user_agent_old(user_agent_str):
    file = join(dirname(dirname(abspath(__file__))), 'user_agent_parser.rb')
    cmd = "ruby %s \"%s\"" % (file, user_agent_str)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    (output, errors) = p.communicate()

    user_agent_data = json.loads(output)

    return {
        'browser_name': user_agent_data[1],
        'browser_version': user_agent_data[2],
        'os_name': user_agent_data[3],
        'os_version': user_agent_data[4],
        'is_bot': user_agent_data[5],
        'bot_name': user_agent_data[6],
        'device_name': user_agent_data[7],
        'device_type': user_agent_data[8],
        'device_brand': user_agent_data[9]
    }

def user_agent(user_agent_str):
    user_agent = parse(user_agent_str)

    return {
        'browser_name': user_agent.browser.family,
        'browser_version': user_agent.browser.version_string,
        'os_name': user_agent.os.family,
        'os_version': user_agent.os.version_string,
        'is_bot': user_agent.is_bot,
        'bot_name': "",
        'device_name': user_agent.device.family,
        'device_type': user_agent.device.model,
        'device_brand': user_agent.device.brand
    }

def week_of_day(datetime_obj):
    week_day_map = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday', 7: 'Sunday'}
    return week_day_map[datetime_obj.isoweekday()]


def date_range(start, end, intv):
    try:
        start = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        start = datetime.strptime(start, "%Y-%m-%d")

    try:
        end = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        end = datetime.strptime(end, "%Y-%m-%d")

    diff = (end - start) / intv
    for i in range(intv):
        yield (start + diff * i).strftime("%Y-%m-%d %H:%M:%S")
    yield end.strftime("%Y-%m-%d %H:%M:%S")


def sort_entry_page(list):
    # list of page rendered event
    list.sort(key=lambda x: x.created_at, reverse=False)


def create_logging_dirs():
    if not os.path.isdir('./lynx_csv'):
        os.makedirs('./lynx_csv')
    if not os.path.isdir('./lynx_errors'):
        os.makedirs('./lynx_errors')


def pull_values(lower_date, upper_date, es_user, es_pw, es_host, es_db, tq_user, tq_pw, tq_host, tq_db):
    create_logging_dirs()

    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    csv_output = './lynx_csv/' + current_time + '_lynx.csv'
    errors_output = './lynx_errors/' + current_time + '_lynx_errors.txt'
    recorded_count = 0
    no_header_yet = True

    # divide up into intervals
    num_intervals = 100
    completed = 0.0
    range_generator = date_range(lower_date, upper_date, num_intervals)
    # remove extra elements
    intervals = list(set(list(range_generator)))
    intervals = sorted(intervals)
    percentage = 100.0 / (len(intervals) - 1)

    engine_url = 'mysql+pymysql://' + es_user + ':' + es_pw + '@' + es_host + '/' + es_db
    es_engine = create_engine(engine_url)

    engine_url = 'mysql+pymysql://' + tq_user + ':' + tq_pw + '@' + tq_host + '/' + tq_db
    tq_engine = create_engine(engine_url)

    metadata = MetaData()
    sessions_table = Table('sessions', metadata, autoload=True, autoload_with=es_engine)
    events_table = Table('events', metadata, autoload=True, autoload_with=es_engine)
    browsers_table = Table('browsers', metadata, autoload=True, autoload_with=es_engine)
    session_attributes_table = Table('session_attributes', metadata, autoload=True, autoload_with=es_engine)
    attributes_table = Table('attributes', metadata, autoload=True, autoload_with=es_engine)
    event_types_table = Table('event_types', metadata, autoload=True, autoload_with=es_engine)
    event_attributes_table = Table('event_attributes', metadata, autoload=True, autoload_with=es_engine)
    forms_table = Table('forms', metadata, autoload=True, autoload_with=es_engine)
    revenues_table = Table('revenues', metadata, autoload=True, autoload_with=es_engine)

    arrival_facts_table = Table('arrival_facts', metadata, autoload=True, autoload_with=tq_engine)

    es_session = load_es_session(es_engine)
    tq_session = load_tq_session(tq_engine)

    attributes_select = es_session.execute(select([attributes_table.c.id, attributes_table.c.name]))
    attributes_table = {}
    for attribute in attributes_select:
        attributes_table[attribute['id']] = attribute['name']

    event_types_select = es_session.execute(select([event_types_table.c.id, event_types_table.c.name]))
    event_types_table = {}
    for attribute in event_types_select:
        event_types_table[attribute['id']] = attribute['name']

    arrival_fact_insert_stmt = arrival_facts_table.insert().values(
        browser_id=bindparam('browser_id'),
        entry_page=bindparam('entry_page'),
        conversion_page=bindparam('conversion_page'),
        conversion=bindparam('conversion'),
        conversion_count=bindparam('conversion_count'),
        event_category=bindparam('event_category'),
        form_city=bindparam('form_city'),
        form_state=bindparam('form_state'),
        form_zip=bindparam('form_zip'),
        prop_own=bindparam('prop_own'),
        user_agent=bindparam('user_agent'),
        browser=bindparam('browser'),
        browser_version=bindparam('browser_version'),
        device_type=bindparam('device_type'),
        utm_source=bindparam('utm_source'),
        utm_campaign=bindparam('utm_campaign'),
        day_of_week=bindparam('day_of_week'),
        os_name=bindparam('os_name'),
        os_version=bindparam('os_version'),
        device_name=bindparam('device_name'),
        device_brand=bindparam('device_brand'),
        ip_address=bindparam('ip_address'),
        gclid=bindparam('gclid'),
        events_count=bindparam('events_count'),
        page_views=bindparam('page_views'),
        conf=bindparam('conf'),
        conu=bindparam('conu'),
        revenue=bindparam('revenue'),
        robot_id=bindparam('robot_id'),
        last_activity=bindparam('last_activity'),
        created_at=bindparam('created_at'),
        session_id=bindparam('session_id')
    )

    arrival_fact_update_stmt = arrival_facts_table.update().where(arrival_facts_table.c.id == bindparam('b_id')).values(
        browser_id=bindparam('browser_id'),
        entry_page=bindparam('entry_page'),
        conversion_page=bindparam('conversion_page'),
        conversion=bindparam('conversion'),
        conversion_count=bindparam('conversion_count'),
        event_category=bindparam('event_category'),
        form_city=bindparam('form_city'),
        form_state=bindparam('form_state'),
        form_zip=bindparam('form_zip'),
        prop_own=bindparam('prop_own'),
        user_agent=bindparam('user_agent'),
        browser=bindparam('browser'),
        browser_version=bindparam('browser_version'),
        device_type=bindparam('device_type'),
        utm_source=bindparam('utm_source'),
        utm_campaign=bindparam('utm_campaign'),
        day_of_week=bindparam('day_of_week'),
        os_name=bindparam('os_name'),
        os_version=bindparam('os_version'),
        device_name=bindparam('device_name'),
        device_brand=bindparam('device_brand'),
        ip_address=bindparam('ip_address'),
        gclid=bindparam('gclid'),
        events_count=bindparam('events_count'),
        page_views=bindparam('page_views'),
        conf=bindparam('conf'),
        conu=bindparam('conu'),
        revenue=bindparam('revenue'),
        robot_id=bindparam('robot_id'),
        last_activity=bindparam('last_activity'),
        created_at=bindparam('created_at'),
        session_id=bindparam('session_id')
    )

    print colored('Pulling Values From Lynx', 'red')
    for index, interval in enumerate(intervals[:-1]):
        print colored("Grabbing for interval (%s)->(%s)" % (intervals[index], intervals[index + 1]), 'blue')
        lower = intervals[index]
        upper = intervals[index + 1]

        session_select = select([sessions_table]).where(sessions_table.c.last_activity > lower).where(
            sessions_table.c.last_activity <= upper)
        session_result = es_session.execute(session_select)

        session_result = [dict(r) for r in session_result]
        session_ids = map(lambda session: session['id'], session_result)

        if len(session_ids) <= 0:
            continue

        children_events_select = select(
            [events_table.c.id, events_table.c.session_id, events_table.c.parent_event_id, events_table.c.event_type_id,
             events_table.c.created_at]).where(
            events_table.c.session_id.in_(session_ids))
        children_events = es_session.execute(children_events_select)
        children_events = [dict(r) for r in children_events]
        for children_event in children_events:
            children_event['event_type'] = event_types_table[children_event['event_type_id']]

        revenue_select = select(
            [revenues_table.c.session_id, revenues_table.c.con_f, revenues_table.c.total_revenue]).where(
            revenues_table.c.session_id.in_(session_ids))
        revenue_result = es_session.execute(revenue_select)
        revenue_result = [dict(r) for r in revenue_result]

        arrival_fact_inserts = []
        arrival_fact_updates = []
        session_count = 0

        for session in session_result:

            session_id = session['id']
            should_update = False

            arrival_fact_id = -1;
            arrival_facts_select = select([arrival_facts_table.c.id, arrival_facts_table.c.last_activity]) \
                .select_from(arrival_facts_table).where(arrival_facts_table.c.session_id == session_id)
            arrival_facts_result = tq_session.execute(arrival_facts_select).fetchone()
            if arrival_facts_result:
                if arrival_facts_result['last_activity'] >= session['last_activity']:
                    continue
                else:
                    arrival_fact_id = arrival_facts_result['id']
                    should_update = True

            session_children = filter(lambda event: event['session_id'] == session_id, children_events)
            if len(session_children) <= 0:
                continue

            user_agent_value = None
            browser_id = None
            browser_name = None
            browser_version = None
            os_name = None
            os_version = None
            robot_id = None
            device_name = None
            device_type = None
            device_brand = None
            ip_address = None
            utm_source = None
            utm_campaign = None
            gclid = None
            form_city = None
            form_state = None
            form_zip = None
            prop_own = None
            conf = 0
            conu = False
            total_revenue = 0

            entry_page = None
            conversion_page = None
            conversion_count = 0

            browser_select = select([browsers_table.c.browser_id]).where(browsers_table.c.id == session['browser_id'])
            browser_id = es_session.execute(browser_select).fetchone()
            if browser_id:
                browser_id = browser_id['browser_id']

            user_agent_value = session['user_agent']
            user_agent_data = user_agent(user_agent_value)
            browser_name = user_agent_data['browser_name']
            browser_version = user_agent_data['browser_version']
            os_name = user_agent_data['os_name']
            os_version = user_agent_data['os_version']
            is_bot = user_agent_data['is_bot']
            bot_name = user_agent_data['bot_name']
            device_name = user_agent_data['device_name']
            device_type = user_agent_data['device_type']
            device_brand = user_agent_data['device_brand']

            ip_address = session['ip']

            revenues = filter(lambda revenue: revenue['session_id'] == session_id, revenue_result)
            if len(revenues) > 0:
                revenue = revenues[0]
                conf = revenue['con_f']
                total_revenue = revenue['total_revenue']
                conu = (conf > 0)

            session_attribute_select = select(
                [session_attributes_table.c.attribute_id, session_attributes_table.c.value]) \
                .where(session_attributes_table.c.session_id == session_id)
            session_attribute_result = es_session.execute(session_attribute_select)
            for session_attribute in session_attribute_result:
                attribute_name = attributes_table[session_attribute['attribute_id']]
                if attribute_name == 'os':
                    if not os_name:
                        os_name = session_attribute['value']
                elif attribute_name == 'utm_source':
                    utm_source = session_attribute['value']
                elif attribute_name == 'utm_campaign':
                    utm_campaign = session_attribute['value']
                elif attribute_name == 'gclid':
                    gclid = session_attribute['value']
                elif attribute_name == 'robot_id':
                    robot_id = session_attribute['value']

            # List of events that belong ot a session
            session_children_event_ids = map(lambda event: event['id'], session_children)
            page_rendered_events = filter(lambda event: event['event_type'] == "Page Rendered", session_children)
            # sort chronologically ascending
            page_rendered_events.sort(key=lambda x: x['created_at'], reverse=False)
            event_attribute_select = select([event_attributes_table.c.event_id, event_attributes_table.c.attribute_id,
                                             event_attributes_table.c.value]) \
                .where(event_attributes_table.c.event_id.in_(session_children_event_ids))
            # page serve event(first one, entry page)
            event_attribute_result = es_session.execute(event_attribute_select)
            event_attribute_result = [dict(r) for r in event_attribute_result]
            for event_attribute in filter(
                    lambda event_attribute: event_attribute['event_id'] == page_rendered_events[0]['id'],
                    event_attribute_result):
                if attributes_table[event_attribute['attribute_id']] == 'page_type':
                    entry_page = event_attribute['value']
                    break

            form_count_select = select([func.count()]).select_from(forms_table).where(
                forms_table.c.session_id == session_id)
            form_count = es_session.execute(form_count_select).scalar()
            if form_count > 0:
                form_select = select(
                    [forms_table.c.event_id, forms_table.c.city, forms_table.c.state, forms_table.c.zip,
                     forms_table.c.property_ownership]).where(forms_table.c.session_id == session_id).order_by(
                    asc(forms_table.c.created_at))
                form_result = es_session.execute(form_select)
                form = form_result.fetchone()
                form_city = form['city']
                form_state = form['state']
                form_zip = form['zip']
                prop_own = form['property_ownership']
                submit_event_ids = [form['event_id']]
                submit_event_ids.extend(map(lambda form: form['event_id'], form_result))
                submit_events = filter(lambda event: event['id'] in submit_event_ids, session_children)
                submit_render_event_ids = map(lambda event: event['parent_event_id'], submit_events)
                relevant_attributes = filter(
                    lambda event_attribute: event_attribute['event_id'] in submit_render_event_ids,
                    event_attribute_result)
                for event_attribute in relevant_attributes:
                    if attributes_table[event_attribute['attribute_id']] == 'page_type':
                        conversion_count += 1
                        conversion_page = event_attribute['value']
                        break

            fact_table = {
                'browser_id': browser_id,
                'entry_page': entry_page,
                'conversion_page': conversion_page,
                'conversion': (conversion_count > 0),
                'conversion_count': conversion_count,
                'event_category': None,
                'form_city': form_city,
                'form_state': form_state,
                'form_zip': form_zip,
                'prop_own': prop_own,
                'user_agent': user_agent_value,
                'browser': browser_name,
                'browser_version': browser_version,
                'device_type': device_type,
                'utm_source': utm_source,
                'utm_campaign': utm_campaign,
                'day_of_week': week_of_day(session['created_at']),
                'os_name': os_name,
                'os_version': os_version,
                'device_name': device_name,
                'device_brand': device_brand,
                'ip_address': ip_address,
                'gclid': gclid,
                'events_count': len(session_children),
                'page_views': len(page_rendered_events),
                'conf': conf,
                'conu': conu,
                'revenue': total_revenue,
                'robot_id': robot_id,
                'last_activity': session['last_activity'],
                'created_at': session['created_at'],
                'session_id': session_id
            }

            if should_update:
                fact_table['b_id'] = arrival_fact_id
                print colored('Update: (%s)' % (fact_table.values()),'green')
                arrival_fact_updates.append(fact_table)
            else:
                print colored('Add: (%s)' % (fact_table.values()),'green')
                arrival_fact_inserts.append(fact_table)

            session_count += 1
            if session_count % 100 == 0:
                print ("Processed %s sessions" % session_count)

                # if len(fact_tables) > 0:
                # with open(csv_output, 'a') as f:  # Just use 'w' mode in 3.x
                #     w = csv.DictWriter(f, fact_tables[0].as_dict().keys())
                #     if no_header_yet :
                #         w.writeheader()
                #         no_header_yet = False
                #
                #     for fact_table in fact_tables:
                #         w.writerow(fact_table.as_dict())
        try:
            if len(arrival_fact_inserts) > 0:
                tq_session.execute(arrival_fact_insert_stmt, arrival_fact_inserts)
                print colored('Planned fact tables added','green')

            if len(arrival_fact_updates) > 0:
                tq_session.execute(arrival_fact_update_stmt, arrival_fact_updates)
                print colored('Planned fact tables updated','green')

            tq_session.commit()
        except:
            e = sys.exc_info()
            with open(errors_output, 'a') as f:
                f.write("%s Records inserted" % recorded_count)
                f.write(str(e))
