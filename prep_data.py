import os
import sqlite3
from dbfread import DBF
import fiona
import csv


root_dir = os.path.dirname(__file__)
data_dir = os.path.join(root_dir, 'data')

db_path = os.path.join(data_dir, 'data.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()

def insert_into_db():


	try:
		c.execute('SELECT * FROM road_names_raw LIMIT 10')

	except sqlite3.OperationalError:
		print 'Creating table road_names_raw'
		c.execute('CREATE TABLE road_names_raw (id integer primary key autoincrement, town text, street_name text)')

		rds_dbf_path = os.path.join(data_dir, 'Emergency_RDS_line.dbf')
		insert_sql = 'INSERT INTO road_names_raw (town, street_name) VALUES (?,?)'

	    # pull only columns 6 and 24
		print 'Reading road data from E911 DBF'
		for record in DBF(rds_dbf_path, 'utf-8', [6, 24]):
			c.execute(insert_sql, (record['LTWN'], record['SN']))

		conn.commit()

	try:
		c.execute('SELECT * FROM town_boundaries_shp LIMIT 10')

	except sqlite3.OperationalError:

		print 'Creating table town_boundaries_shp and inserting FIPS6 and townname data'
		c.execute('CREATE TABLE town_boundaries_shp (id integer primary key autoincrement, fips text, town text)')

		town_dbf_path = os.path.join(data_dir, 'Boundary_TWNBNDS_poly.dbf')
		insert_sql = 'INSERT INTO town_boundaries_shp (fips, town) VALUES (?,?)'

	    # pull only columns 6 and 24
		for record in DBF(town_dbf_path, 'utf-8', [0, 1]):
			c.execute(insert_sql, (record['FIPS6'], record['TOWNNAME']))

		conn.commit()


def update_town_names():

	print 'Attempted to join towns from road data to towns from boundary data'
	unmatched_towns_sql = 'SELECT road_names_raw.town ' \
	                      'FROM road_names_raw  ' \
					      'LEFT OUTER JOIN town_boundaries_shp ON road_names_raw.town = town_boundaries_shp.town ' \
					      'WHERE town_boundaries_shp.town IS NULL ' \
					      'GROUP BY road_names_raw.town'

	
	unmatched_rows = c.execute(unmatched_towns_sql).fetchall()

	if unmatched_rows:
		print 'Unmatched towns found. Deleting/updating as necessary. Rows:'
		print [u for u in unmatched_rows]

	delete_list = ['CAUCA, QUEBEC, CA', 'COOS COUNTY, NH', 'WASHINGTON COUNTY, NY']

	for delete_town in delete_list:
		c.execute('DELETE FROM road_names_raw WHERE town = ?', (delete_town,))

	update_dict = {'BELLOWS FALLS': 'ROCKINGHAM', 'ENOSBURGH': 'ENOSBURG', 'ESSEX JUNCTION VILLAGE': 'ESSEX',
	               'ESSEX TOWN': 'ESSEX', 'NORTH BENNINGTON': 'BENNINGTON', 'ORLEANS': 'BARTON',
	               'RUTLAND TOWN': 'RUTLAND', 'SAINT ALBANS CITY': 'ST. ALBANS CITY',
	               'SAINT ALBANS TOWN': 'ST. ALBANS TOWN', 'SAINT GEORGE': 'ST. GEORGE', 
	               'SAINT JOHNSBURY': 'ST. JOHNSBURY', 'SAXTONS RIVER': 'ROCKINGHAM', 
	               'WARRENS GORE': 'WARREN GORE', 'WEST PAWLET': 'PAWLET'}

	for current_town, updated_town in update_dict.iteritems():
		c.execute('UPDATE road_names_raw SET town = ? WHERE town=?', (updated_town, current_town))

	conn.commit()

	unmatched_rows = c.execute(unmatched_towns_sql).fetchall()

	if unmatched_rows:
		raise ValueError("Some road_names_raw don't match Boundary_TWNBNDS_poly")


def tokenize():

	try:
		c.execute('SELECT * FROM words_by_town LIMIT 10')

	except sqlite3.OperationalError:
		c.execute('CREATE TABLE words_by_town (id integer primary key autoincrement, town text, word text)')

		# Important to group by street_name and town here-- don't want to double count
		# multiple sections of MAIN ST. This is GIS data, after all
		rows = c.execute('SELECT street_name, town FROM road_names_raw GROUP BY street_name, town').fetchall()

		insert_str = ('INSERT INTO words_by_town (town, word) VALUES (?, ?)')

		skip_words = ['ROUTE', 'VT', 'INTERSTATE', 'US', 'STATE', 'HWY', 'EXT', 'ENT', 'SFH', 
					  'EXIT', 'ENTRACE', 'ST', 'RD', 'THE', 'U', 'TURN']

		for row in rows:
			word_list = row[0].split()
			town = row[1]

			word_list = filter(lambda w: w not in skip_words, word_list)

			for word in word_list:

				# Filter out route numbers
				try:
					int(word)

				except:
					c.execute(insert_str, (town, word))

		conn.commit()

	print 'Word counts statewide: '
	print c.execute('SELECT word, count(word) as count FROM words_by_town GROUP BY word ORDER BY count DESC LIMIT 100').fetchall()


def write_lookup_titlecase():

	boundary_shp = os.path.join(data_dir, 'Boundary_TWNBNDS_poly.shp')
	fips_lookup = os.path.join(data_dir, 'fips6_lookup.csv')

	with fiona.open(boundary_shp) as source:
		with open(fips_lookup, 'wb') as csvFile:
			csvWriter = csv.writer(csvFile)
			csvWriter.writerow(['fips6', 'town'])

			for feature in source:
				att_dict = feature['properties']
				fips_val = att_dict['FIPS6']
				town_title_case = att_dict['TOWNNAME'].title()
				
				csvWriter.writerow([fips_val, town_title_case])





if __name__ == '__main__':
	insert_into_db()

	update_town_names()

	tokenize()

	write_lookup_titlecase()


# GROUP By word, town and COUNT