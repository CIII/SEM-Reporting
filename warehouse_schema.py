"""Warehouse Schema"""

__copyright__ = "Copyright (C) 2016 TapQuality"
__docformat__ = "restructuredtext"

import mysql.connector
from warehouse import arrival_facts

fact_tables = [arrival_facts, ]

tq_reporting = mysql.connector.connect(option_files='tqreportingdb.cnf')
try:
	tqr_cursor = tq_reporting.cursor()

	for fact_table in fact_tables:
		tqr_cursor.execute(fact_table.drop_table())
		tqr_cursor.execute(fact_table.create_table())

finally:
	tq_reporting.close()
