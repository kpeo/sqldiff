#!/usr/bin/python

# Copyright (C) 2014-2018 Vladimir Yakunin (kpeo) <kpeo.y3k@gmail.com>
#
# The redistribution terms are provided in the LICENSE file
# that must be distributed with this source code.

import argparse
import sqldiff

print('sqldiff: Compare database object between databases / DDL-files\n')
parser = argparse.ArgumentParser()
parser.add_argument('left', help='left source for compare: db:<connection_string> or dir:<SQLDIR_MAIN>', type=str)
parser.add_argument('right', help='right source for compare: db:<connection_string> or dir:<SQLDIR_MAIN>', type=str)
parser.add_argument('--right', dest='rightonly', action='store_true', help='only difference for right argument')
parser.add_argument('--left', dest='leftonly', action='store_true', help='only difference for left argument')
parser.add_argument('--tables', dest='tables', action='store_true', help='compare only for tables')
parser.add_argument('--no-tables', dest='tables', action='store_false', help='compare all but tables (default)')
parser.add_argument('--print', dest='show', action='store_true', help='print results')

parser.set_defaults(tables=False)
parser.set_defaults(show=False)
parser.set_defaults(rightonly=False)
parser.set_defaults(leftonly=False)

args = parser.parse_args()

if not args.left and not args.right:
	parser.print_help()

print "Compare", args.left, "width", args.right
diff_args = (args.left, args.right)
objects = []

for arg in diff_args:
	if arg.split(":")[0] == 'db':
		if args.tables:
			objects.append(sqldiff.get_db_tables())
		else:
			objects.append(sqldiff.get_db_objects())
	elif arg.split(":")[0] == 'dir':
		if args.tables:
			objects.append(sqldiff.get_file_tables())
		else:
			objects.append(sqldiff.get_file_objects())
	else:
		print "Can't proceed with", arg


if args.show:
	if args.left:
		print "<<<", args.left
#		print objects[0]
	if args.right:
		print ">>>", args.right
#		print objects[1]

objkeys = set(objects[0].keys() + objects[1].keys())
for key in objkeys:
	try:
		assert(objects[0][key])
	except:
		print "<<<", key
		continue
	try:
		assert(objects[1][key])
	except:
		print ">>>", key
		continue
		

	print "===", key, ":"
	tmp = sqldiff.diff(objects[0][key],objects[1][key])
	if not args.rightonly:
		for el in tmp[0]:
			print "<<<", el
	if not args.leftonly:
		for el in tmp[1]:
			print ">>>", el

#print sqldiff.diff(objects[0], objects[1])
#print get_file_tables()
#print get_db_tables()
#print get_file_objects()
#save_objects('tables.json', get_db_tables())

