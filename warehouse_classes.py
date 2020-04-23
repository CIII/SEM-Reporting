"""Warehouse Classes"""

__copyright__ = "Copyright (C) 2016 TapQuality"
__docformat__ = "restructuredtext"

class Field:
	data = ''
	def __init__(self, name, schema, numeric=False):
		self.name = name
		self.schema = schema
		self.numeric = numeric

	def insert_data(self):
		if self.numeric or self.data is None:
			sql = "%s" % self.get_data()
		else:
			sql = "'%s'" % self.get_data()
		return sql

	def get_data(self):
		if self.data is None:
			return "NULL"
		else:
			return self.data

class FactTable:
	def __init__(self, name, dimensions, measures):
		self.name = name
		self.dimensions = dimensions
		self.measures = measures

	def create_table(self):
		sql = "CREATE TABLE `%s` (" % self.name
		sql += "`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT, "

		for field in self.dimensions + self.measures:
			sql += "`%s` %s, " % (field.name, field.schema)

		sql += "PRIMARY KEY (`id`)) ENGINE=InnoDB"
		return sql

	def drop_table(self):
		sql = "DROP TABLE IF EXISTS %s" % self.name
		return sql

	def add_indexes(self):
		pass

	def insert_data(self):
		sql = "INSERT INTO %s (" % self.name
		first = True
		for field in self.dimensions + self.measures:
			if first:
				sql += "%s" % field.name
				first = False
			else:
				sql += ", %s" % field.name
		sql += ") VALUES("
		first = True
		for field in self.dimensions + self.measures:
			if first:
				sql += field.insert_data()
				first = False
			else:
				sql += ", %s" % field.insert_data()
		sql += ")"
		return sql

	def clear_data(self):
		for field in self.dimensions + self.measures:
			field.data = ''





