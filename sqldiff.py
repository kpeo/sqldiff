# Copyright (C) 2014-2018 Vladimir Yakunin (kpeo) <kpeo.y3k@gmail.com>
#
# The redistribution terms are provided in the LICENSE file
# that must be distributed with this source code.

from os import walk 
import time
import cx_Oracle
import sqlparse
import argparse
try:
	import json
except ImportError:
	import simplejson as json
from settings import SQL_CONNECT, SQLDB_TYPES, SQLDIR_MAIN, SQLDIR_PATHS, SQLDIR_MAP


# 1. diff between object names (DB & DDL)
# 2. diff between table columns (DB & DDL)
# 3. diff between table columns definitions (DB & DDL)
# 4. diff between table fillings (only for DB)

def diff(a, b):
	a = set(a)
	b = set(b)
	return [a.difference(b), b.difference(a)]
#	return [aa for aa in a if aa not in b]

def extract_definitions(token_list):
    # assumes that token_list is a parenthesis
    definitions = []
    # grab the first token, ignoring whitespace
    token = token_list.token_next(0)
    tmp = []
    while token and not token.match(sqlparse.tokens.Punctuation, ')'):
        tmp.append(token)
        idx = token_list.token_index(token)
        # grab the next token, this times including whitespace
        token = token_list.token_next(idx, skip_ws=False)
        # split on ","
        if (token is not None  # = end of statement
            and token.match(sqlparse.tokens.Punctuation, ',')):
            definitions.append(tmp)
            tmp = []
            idx = token_list.token_index(token)
            token = token_list.token_next(idx)
    if tmp and isinstance(tmp[0], sqlparse.sql.Identifier):
        definitions.append(tmp)
    return definitions

# return ((TABLE_NAME : COLUMN_NAME1,DEFINITION1),(COLUMN_NAME2,DEFINITION2),...)
def get_file_table_columns(sql, definitions=False):
        parsed = sqlparse.parse(sql.replace('&','_'))[0]

	tmpl = ()
	tmp = []
	res = {}
	
        # extract the parenthesis which holds column definitions (workaround)
        par = parsed.token_next_by_instance(0, sqlparse.sql.Function)
        # parse table name before parenthesis

	if(not par):
		return res

	table_name = par.value.split('(')[0].strip().upper()

        par = par.token_next_by_instance(0, sqlparse.sql.Parenthesis)

        columns = extract_definitions(par)

        for column in columns:
		if definitions:
			tmpl = ( column[0].value.strip().upper(), ''.join(str(t).strip().upper()+' ' for t in column[1:]) )
			tmp.append(tmpl)
		else:
			tmp.append(column[0].value.strip().upper())
	
	res[table_name] = tmp
	
	return res

def parse_triggers(sql):
	return ""

def get_file_func(sql):
	parsed = sqlparse.parse(sql.replace('&','_'))[0]
	par = parsed.token_next_by_instance(0, sqlparse.sql.Function)
	if(not par):
		return res
	return par.value.split('(')[0].strip().upper()

# return DDL-tables dictionary with optional definitions
# {TABLE_NAME : [COLUMN1, COLUMN2, ...]}
# or
# {TABLE_NAME : [(COLUMN1, DEFINITION1), (COLUMN2, DEFINITION2), ...]}
def get_file_tables(definitions=False):
	tables = {}
	for path in SQLDIR_PATHS:
		filelist = []
		for ( _, _, filenames ) in walk(SQLDIR_MAIN + path + '/tables'):
			filelist.extend(filenames)
			break
		for file in sorted(filelist):
			if(file.split('.')[1].upper() == 'TAB'):
				f = open(SQLDIR_MAIN + path + '/tables/' + file, 'r')
				data = f.read().replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
				
				tables.update( get_file_table_columns(data, definitions) )
				f.close()
	return tables

# return DB-tables dictionary with optional definitions:
# {TABLE_NAME : [COLUMN1, COLUMN2, ...]}
# or
# {TABLE_NAME : [(COLUMN1, DEFINITION1), (COLUMN2, DEFINITION2), ...]}
def get_db_tables(definitions=False):
	tables = {}
	res = []
	con = cx_Oracle.connect(SQL_CONNECT)
	cur = con.cursor()
	cur2 = con.cursor()
	cur.execute("select object_name from dba_objects where owner='SBAZ' and object_type='TABLE' order by object_name")
	for r in cur:
		if definitions:
			#WARNING: This option is not completely supported
			query = "select column_name,data_type,data_length,nullable,data_default from all_tab_columns where owner='SBAZ' and table_name=:tablename order by column_id"
			params = {'tablename' : r[0]}
			cur2.execute(query, params)
			for row in cur2:
				len = ''
				defval = ''
				nulval = ''
				if row[2] and row[2] != '':
					len = '(' + str(row[2]) + ')'
				if row[4] and row[4] != '':
					defval = ' DEFAULT ' + str(row[4]).strip()
				if row[3] and row[3] != '':
					if row[3] == 'N':
						nulval = ' NOT NULL'

				tmpstr = row[0] + ' ' + row[1] + len + defval + nulval
				res.append(tmpstr)
		else:
			query = "select column_name from all_tab_columns where owner='SBAZ' and table_name=:tablename order by column_id"
			params = {'tablename' : r[0]}
			cur2.execute(query, params)
			for row in cur2:
				res.append(row[0])
		tables[r[0]] = res
	cur2.close
	cur.close
	con.close
	return tables

# return dictionary with DB objects names (by its type):
# {SQLDB_TYPE : [OBJECT_NAME1, OBJECT_NAME2, ...]}
def get_db_objects():
	db_objects = {}
	con = cx_Oracle.connect(SQL_CONNECT)
	cur = con.cursor()
	cur.execute("select object_type, object_name from dba_objects where owner='SBAZ' order by object_type, object_name")
	for r in cur:
		for t in SQLDB_TYPES:
			if r[0] == t:
				if t in db_objects.keys():
					db_objects[t].append(r[1])
				else:
					db_objects[t] = [r[1]]
	cur.close
	con.close
	return db_objects	

# return dictionary with DDL objects names (by its type):
# {SQLDB_TYPE : [OBJECT_NAME1, OBJECT_NAME2, ...]}
def get_file_objects():
	file_objects = {}
        for path in SQLDIR_PATHS:
		for key in SQLDIR_MAP: 
			filelist = []
	                for ( _, _, filenames ) in walk(SQLDIR_MAIN + path + '/' + key):
        	                filelist.extend(filenames)
                	        break
	                for file in sorted(filelist):
				for ext in SQLDIR_MAP[key]:
					if file.split('.')[1] and file.split('.')[1].upper() == ext[0]:
		                                f = open(SQLDIR_MAIN + path + '/' + key + '/' + file, 'r')
                		                data = f.read().replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
						if ext[1] in file_objects.keys():
							file_objects[ext[1]].append(file.split('.')[0].upper())
						else:
							file_objects[ext[1]] = [file.split('.')[0].upper()]
						f.close()
        return file_objects

# save dictionary to JSON-file
def save_objects(file, list):
	f = open(file, 'w')
	json.dumps(list, f)
	f.close()

# load dictionary from JSON-file
def load_objects(file, list):
	f = open(file, 'r')
	list = json.load(f)
	f.close()

