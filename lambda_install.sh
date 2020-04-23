#!/bin/bash

virtualenv .
source bin/activate
pip install sqlalchemy
pip install pymysql
pip install termcolor
pip install pyyaml ua-parser user-agents

cp -r lib/python2.7/site-packages/* .
rm -rf lib

result=${PWD##*/}
timestamp=$(date +%Y%m%d_%k%M%S)
zip -r $result$timestamp.zip * -x *.zip*
deactivate