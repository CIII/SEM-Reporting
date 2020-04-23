#!/bin/bash

#install dependencies
sudo apt-get install python-dev
sudo apt-get install python2.7-dev
sudo apt-get install python-pip
sudo apt-get install ruby
sudo apt-get install ruby-bundler
sudo apt-get install mysql-connector-python

#ruby gem dependencies
sudo gem install device_detector

#python pip dependencies
dep=(
	"ipython"
	"ipdb"
	"googleads"
	"pytz"
	"termcolor"
	"sqlalchemy"
	"pymysql"
	"boto3"
	"pyyaml"
	"ua-parser"
	"user-agents"
	)

TEMP=`getopt -u --long without $*`
set -- $TEMP
for i; do
	case "$i" in
	--without)
		dep=(${dep[@]//${3}*/})
		jjshift ;;
	esac
done

#install pip dependencies
for p in "${dep[@]}"; do
    echo "install ${p}"
	pip install $p;
	code=$?; if [[ $code != 0 ]]; then exit $code; fi
done

