from boto3.s3.transfer import S3Transfer
import boto3
import subprocess
import ConfigParser
from datetime import datetime
import os
import zipfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import lynx.tables as tables
from termcolor import colored

es_cnf = ''

def load_lynx_session(es_engine):
    """"""
    Session = sessionmaker(bind=es_engine)
    session = Session()
    return session


def clean_dir(dir):
    filelist = [f for f in os.listdir(dir) if f.endswith(".txt") and f.startswith('robot')]
    for f in filelist:
        os.remove(dir + f)


def zip_dir(dir, zip_name):
    zip = zipfile.ZipFile(zip_name, 'w')
    filelist = [f for f in os.listdir(dir) if f.endswith(".txt") and f.startswith('robot')]
    for f in filelist:
        get_file = dir + f
        zip.write(get_file)

def import_zip_to_s3(zip_file):

    print colored("Uploading %s to S3" % zip_file, 'green')

    access_key = 'AKIAJ4M3Y4LM3RAAAOKA'
    secret_key = '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'

    transfer = S3Transfer(boto3.client('s3',aws_access_key_id=access_key,
                                       aws_secret_access_key=secret_key))
    key = 'db_cleanup/' + os.path.basename(zip_file)
    transfer.upload_file(zip_file, 'easiersolar', key)

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def clean_lynx(lower, upper, es_user, es_pw, es_host, es_db, tq_user, tq_pw, tq_host, tq_db):
    print "Beginning clean up of lynx"
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    robot_sessions_dump_file = '/tmp/' + current_time + '_robot_lynx_sessions_dump.txt'
    robot_sessions_dump = open(robot_sessions_dump_file, 'a+')
    robot_forms_dump_file = '/tmp/' + current_time + '_robot_lynx_forms_dump.txt'
    robot_forms_dump = open(robot_forms_dump_file, 'a+')
    robot_session_attributes_dump_file = '/tmp/' + current_time + '_robot_lynx_session_attributes_dump.txt'
    robot_session_attributes_dump = open(robot_session_attributes_dump_file, 'a+')
    robot_events_dump_file = '/tmp/' + current_time + '_robot_lynx_events_dump.txt'
    robot_events_dump = open(robot_events_dump_file, 'a+')
    robot_event_attributes_dump_file = '/tmp/' + current_time + '_robot_lynx_event_attributes_dump.txt'
    robot_event_attributes_dump = open(robot_event_attributes_dump_file, 'a+')

    config = ConfigParser.ConfigParser()
    config.read(es_cnf)

    engine_url = 'mysql+pymysql://' + es_user + ':' + es_pw + '@' + es_host + '/' + es_db
    es_engine = create_engine(engine_url)
    lynx_session = load_lynx_session(es_engine)

    robot_session_attributes_1 = lynx_session.query(tables.SessionAttributes.session_id) \
        .filter(tables.SessionAttributes.created_at.between(lower, upper)) \
        .filter(tables.SessionAttributes.attribute_id == '12').all()
    robot_session_ids_total = map(lambda x: x[0], robot_session_attributes_1)

    #Need to change to last activity
    robot_session_ids_is_robot = lynx_session.query(tables.Sessions.id).filter(tables.Sessions.last_activity.between(lower, upper)) \
        .filter(tables.Sessions.is_robot).all()
    robot_session_ids_is_robot = map(lambda x: x[0], robot_session_ids_is_robot)
    robot_session_ids_total.extend(robot_session_ids_is_robot)
    robot_session_ids_total = list(chunks(robot_session_ids_total,100))

    count = 1
    for robot_session_ids in robot_session_ids_total:
        print colored('Recording part %s' % count, 'blue')
        print 'Recording/Persisting Robot Events'
        robot_event_ids = []
        for event in lynx_session.query(
                tables.Events.id,
                tables.Events.session_id,
                tables.Events.event_type_id,
                tables.Events.parent_event_id,
                tables.Events.created_at).filter(tables.Events.session_id.in_(robot_session_ids)).yield_per(5):
            robot_event_ids.append(event[0])
            robot_events_dump.write('|'.join(('"' + str(x) + '"') for x in event))
            robot_events_dump.write("\n")

        print 'Recording/Persisting Robot EventAttributes'
        for event_attribute in lynx_session.query(
                tables.EventAttributes.id,
                tables.EventAttributes.event_id,
                tables.EventAttributes.attribute_id,
                tables.EventAttributes.value).filter(tables.EventAttributes.event_id.in_(robot_event_ids)).yield_per(5):
            robot_event_attributes_dump.write('|'.join(('"' + str(x) + '"') for x in event_attribute))
            robot_event_attributes_dump.write("\n")

        print 'Recording/Persisting Robot Forms'
        for form in lynx_session.query(
                tables.Forms.id,
                tables.Forms.event_id,
                tables.Forms.first_name,
                tables.Forms.last_name,
                tables.Forms.email,
                tables.Forms.street,
                tables.Forms.city,
                tables.Forms.state,
                tables.Forms.zip,
                tables.Forms.property_ownership,
                tables.Forms.electric_bill,
                tables.Forms.electric_company,
                tables.Forms.phone_home,
                tables.Forms.leadid_token,
                tables.Forms.domtok,
                tables.Forms.ref,
                tables.Forms.xxTrustedFormCertUrl,
                tables.Forms.xxTrustedFormToken,
                tables.Forms.created_at).filter(tables.Forms.event_id.in_(robot_event_ids)).yield_per(5):
            robot_forms_dump.write('|'.join(('"' + str(x) + '"') for x in form))
            robot_forms_dump.write("\n")

        print 'Recording/Persisiting Robot Session Attributes'
        for session_attribute in lynx_session.query(
                tables.SessionAttributes.id, tables.SessionAttributes.session_id,
                tables.SessionAttributes.attribute_id,
                tables.SessionAttributes.value,
                tables.SessionAttributes.created_at).filter(
            tables.SessionAttributes.session_id.in_(robot_session_ids)).all():
            robot_session_attributes_dump.write('|'.join(('"' + str(x) + '"') for x in session_attribute))
            robot_session_attributes_dump.write("\n")

        print 'Recording/Persisting Robot Sessions'
        for session in lynx_session.query(
                tables.Sessions.id,
                tables.Sessions.browser_id,
                tables.Sessions.user_agent,
                tables.Sessions.created_at,
                tables.Sessions.last_activity).filter(tables.Sessions.id.in_(robot_session_ids)).yield_per(5):
            robot_sessions_dump.write('|'.join(('"' + str(x) + '"') for x in session))
            robot_sessions_dump.write("\n")

        robot_sessions_dump.flush()
        robot_forms_dump.flush()
        robot_session_attributes_dump.flush()
        robot_events_dump.flush()
        robot_event_attributes_dump.flush()

        lynx_session.expunge_all()
        count += 1

        # Delete robots
        print colored('Deleting robot events', 'red')
        lynx_session.query(tables.Events).filter(tables.Events.session_id.in_(robot_session_ids)).delete(
            synchronize_session=False)
        lynx_session.expire_all()
        print colored('Deleting robot event attributes', 'red')
        lynx_session.query(tables.EventAttributes).filter(tables.EventAttributes.event_id.in_(robot_event_ids)).delete(
            synchronize_session=False)
        lynx_session.expire_all()
        print colored('Deleting robot forms', 'red')
        lynx_session.query(tables.Forms).filter(tables.Forms.event_id.in_(robot_event_ids)).delete(
            synchronize_session=False)
        lynx_session.expire_all()
        print colored('Deleting robot session attributes', 'red')
        lynx_session.query(tables.SessionAttributes).filter(tables.SessionAttributes.session_id.in_(robot_session_ids)) \
            .delete(synchronize_session=False)
        lynx_session.expire_all()
        print colored('Deleting robot sessions', 'red')
        lynx_session.query(tables.Sessions).filter(tables.Sessions.id.in_(robot_session_ids)).delete(
            synchronize_session=False)
        lynx_session.expire_all()
        lynx_session.commit()

    lynx_session.close()

    # Zip files and delete txt files
    robot_lynx_zip = '/tmp/' + current_time + '_robot_lynx.zip'
    zip = zipfile.ZipFile(robot_lynx_zip, 'w')
    zip.write(robot_sessions_dump_file)
    zip.write(robot_forms_dump_file)
    zip.write(robot_session_attributes_dump_file)
    zip.write(robot_events_dump_file)
    zip.write(robot_event_attributes_dump_file)

    import_zip_to_s3(robot_lynx_zip)

    os.remove(robot_sessions_dump_file)
    os.remove(robot_forms_dump_file)
    os.remove(robot_session_attributes_dump_file)
    os.remove(robot_events_dump_file)
    os.remove(robot_event_attributes_dump_file)
