===========
DBMS - DataBases Made Simpler
===========

DBMS is a database adapter that wraps and provides
uniform interface to other DB API compliant adapters. 

It manages connections, doing automatic imports and providing a
uniform connection method to most common databases.
Implements DictCursor, NamedTupleCursor and OrderedDictCursor.

It currently supports IBM DB2, Firebird, MSSQL Server, MySQL, Oracle,
PostgreSQL, SQLite and ODBC connections.

Sample usage::
	>>> import dbms
	>>> db = dbms.connect.postgres('UserName', 'SuperSecret', 'Chinook')
	>>> cur = db.cursor()
	>>> cur.execute('SELECT * FROM artist WHERE artistid = %s', (101,))
	>>> row = cur.fetchone()
	>>> row.pprint()
	artistid : 101
	name     : Lulu Santos
	
	# Database Inspection
	>>> db.inspect.tables()
	['album', 'artist', 'customer', 'employee', 'genre', 'invoice', 'invoiceline', 'mediatype', 'playlist', 'playlisttrack', 'track']
	>>> db.inspect.columns('album')
	['albumid', 'title', 'artistid']
	>>> db.probe.getColumns('album')
	[Record('albumid', 'integer', 'N', 'Y'), 
	Record('title', 'character varying', 'N', None), 
	Record('artistid', 'integer', 'N', None)]
	
	# Saved connections
	>>> dbms.servers.list()
	['ChinookPg', 'ChinookLTE']
	# open saved connection
	>>> db = dbms.servers.open('ChinookPg')
	Enter master password:
	********
	
	# logged cursor
	>>> cur = db.loggedCursor()
	>>> cur.execute('SELECT * FROM "Album" WHERE "ArtistId" = %s', (1,))
	>>> dbms.logger.view(limit=1)
	[Record('2014-07-01 08:11:48', 'ChinookPg', 'SELECT * FROM "Album" WHERE "ArtistId" = %s', (1))]
	
	# utilities
	>>> from dbms import utils
	>>> query, params = utils.formatQuery(('SELECT * FROM Album WHERE ArtistId = ',
			Param(1),
			'AND AlbumId < ',
			NamedParam('maxAlbumId', 50)),
			cur.paramstyle)
	>>> cur.execute(query, params)
	>>> utils.cursorToXLSX(cur, '/tmp/AlbumList.xlsx')
	>>> cur.execute('SELECT * FROM Album')
	>>> utils.cursorToCursorCopy(cur, destCur, 'album')
	>>> query = 'SELECT * FROM artist WHERE artistid BETWEEN %s AND %s'
	>>> cur.execute(query, (100, 105))
	>>> utils.cursorToJSON(cur)
	[
	{"artistid": 100, "name": "Lenny Kravitz"},
	{"artistid": 101, "name": "Lulu Santos"},
	{"artistid": 102, "name": "Marillion"},
	{"artistid": 103, "name": "Marisa Monte"},
	{"artistid": 104, "name": "Marvin Gaye"},
	{"artistid": 105, "name": "Men At Work"},
	]
	>>> cur.execute(query, (100, 105))
	>>> utils.cursorToFixedWidth(cur)
	ARTISTID  NAME            
	100       Lenny Kravitz   
	101       Lulu Santos     
	102       Marillion       
	103       Marisa Monte    
	104       Marvin Gaye     
	105       Men At Work 
	
	