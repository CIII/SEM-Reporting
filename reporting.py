import lynx.lynx as Lynx
import db_cleanup.robot_lynx as RobotLynx
import sys
import optparse
import os
import ConfigParser
import datetime

def main():

    parser = optparse.OptionParser()

    parser.add_option('-c', '--clean',
                      action="store_true", dest="clean",
                      help="clean up robots")

    options, args = parser.parse_args()
    try:
        lower = args[0]
        upper =  args[1]

        es_cnf = args[2]
        tq_cnf = args[3]
    except:
        print 'Incorrect inputs. Require'
        print 'python reporting.py [options] <lower> <upper> <easiersolar_conf> <tqreporting_conf>'
        sys.exit()

    config = ConfigParser.ConfigParser()
    config.read(es_cnf)
    lynx_user = config.get('connector_python', 'user')
    lynx_pw = config.get('connector_python', 'password')
    lynx_host = config.get('connector_python', 'host')
    lynx_db = config.get('connector_python', 'database')
    config.read(tq_cnf)
    tq_user = config.get('connector_python', 'user')
    tq_pw = config.get('connector_python', 'password')
    tq_host = config.get('connector_python', 'host')
    tq_db = config.get('connector_python', 'database')

    if options.clean :
        print 'Cleaning Lynx'
        RobotLynx.es_cnf = es_cnf
        RobotLynx.clean_lynx(lower,upper)

    Lynx.es_cnf = es_cnf
    Lynx.tq_cnf = tq_cnf

    Lynx.pull_values(lower_date=lower, upper_date=upper, es_user=lynx_user, es_pw=lynx_pw, es_host=lynx_host,
                     es_db=lynx_db, tq_user=tq_user, tq_pw=tq_pw, tq_host=tq_host, tq_db=tq_db)

def lambda_handler(event, context):

    try:
        gap = os.environ['DAYS_GAP']
        duration = os.environ['FETCH_DURATION']

        lynx_user = os.environ['LYNX_USER']
        lynx_pw = os.environ['LYNX_PW']
        lynx_host = os.environ['LYNX_HOST']
        lynx_db = os.environ['LYNX_DB']

        tq_user = os.environ['TQ_USER']
        tq_pw = os.environ['TQ_PW']
        tq_host = os.environ['TQ_HOST']
        tq_db = os.environ['TQ_DB']

    except KeyError, e:
        print e
        sys.exit("Missing configurations")

    current_time = datetime.datetime.now()
    end_time = current_time - datetime.timedelta(days=int(gap))
    upper = end_time.strftime('%Y-%m-%d %H:%M:%S')
    start_time = end_time - datetime.timedelta(hours=int(duration))
    lower = start_time.strftime('%Y-%m-%d %H:%M:%S')
    RobotLynx.clean_lynx(lower=lower, upper=upper, es_user=lynx_user, es_pw=lynx_pw, es_host=lynx_host,
                         es_db=lynx_db, tq_user=tq_user, tq_pw=tq_pw, tq_host=tq_host, tq_db=tq_db)
    Lynx.pull_values(lower_date=lower, upper_date=upper, es_user=lynx_user, es_pw=lynx_pw, es_host=lynx_host,
                     es_db=lynx_db, tq_user=tq_user, tq_pw=tq_pw, tq_host=tq_host, tq_db=tq_db)

if __name__ == "__main__":
    main()