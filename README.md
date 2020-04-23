# Reporting
Search Engine Marketing Reporting


Ubuntu Installation
-------------------

0. Clone this repo to target destination.
0. Copy/create db config files for the sitebrain, leadpath, easiersolar(lynx), and tqreporting dbs.
0. Copy/create googleads.yaml for adwords api calls. Default location is the home dir
0. Create the file `/etc/apt/sources.list.d/mysql.list` containing the line `deb http://repo.mysql.com/apt/ubuntu/ trusty connector-python-2.0` (note that this is for `trusty` or Ubuntu 14.04 -- adjust as needed)
0. `sudo apt-key adv --keyserver pgp.mit.edu --recv-keys 5072E1F5`
0. `sudo apt-get update`
0. from the reporting repo run `sudo ./install_packages.sh`
0. verify/change table names in warehouse.py for effecting production/staging tables
0. use `cronfile` text file as the basis for a cron


Current Deployment
------------------

This application is deployed on the sever labeled "staging" in the EC2 dashboard. It runs as a cron under the user "ubuntu":
```
0 * * * * cd /home/ubuntu/Reporting/ && python arrival_fact_etl.py
```
This action benchmarks itself and will upload all not-uploaded data to Google Data Whatever by first querying the MAX(updated_at) from Google. Service interruption should not result in lost data.


AdWords
-------

**UNDER CONSTRUCTION**
