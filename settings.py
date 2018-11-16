# Copyright (C) 2014-2018 Vladimir Yakunin (kpeo) <kpeo.y3k@gmail.com>
#
# The redistribution terms are provided in the LICENSE file
# that must be distributed with this source code.

SQL_CONNECT = 'test/test@127.0.0.1/orcl'

SQLDIR_MAIN = '/home/oracle/source'
SQLDIR_PATHS = (
	'/dbobjects',
)

SQLDIR_MAP = {
	'directories':	(['PDC','DIRECTORY'],),
	'functions':	(['FNC','FUNCTION'],),
	'links':	(['SQL',''],),
	'packages':	(['SPC','PACKAGE'], ['BDY','PACKAGE BODY']),
	'procedures':	(['PRC','PROCEDURE']),
	'queues':	(['SQL','QUEUE'],),
	'roles':	(['SQL','RULE'],),
	'sequences':	(['SEQ','SEQUENCE'],),
	'synonyms':	(['SQL','SYNONYM'],),
	'tables':	(['TAB','TABLE'],),
	'triggers':	(['TRG','TRIGGER'],),
	'types':	(['TPS','TYPE'],['TPB','TYPE BODY']),
	'view':		(['SQL',''],)
}

SQLDB_TYPES = (
	'DIRECTORY',
	'FUNCTION',
	'INDEX',
	'PACKAGE',
	'PACKAGE BODY',
	'PROCEDURE',
	'QUEUE',
	'RULE',
	'SEQUENCE',
	'SYNONYM',
	'TABLE',
	'TRIGGER',
	'TYPE',
	'TYPE BODY',
)
