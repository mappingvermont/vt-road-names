import os
import sqlite3
import json
import subprocess
from collections import Counter


data_dir = os.path.dirname(__file__)
source_dir = os.path.join(data_dir, 'source')

db_path = os.path.join(data_dir, 'data.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()

def shape_to_geojson():

	shp_path = os.path.join(source_dir, 'Boundary_TWNBNDS_poly.shp')
	geojson_path = os.path.join(data_dir, 'town_boundaries.geojson')

	# Need to remove this first, ogr2ogr can't -overwrite geojson
	if os.path.exists(geojson_path):
		os.remove(geojson_path)

	cmd = ['ogr2ogr','-f', 'GeoJSON', '-t_srs', 'EPSG:4326', geojson_path, shp_path]
	subprocess.check_call(cmd)

	return geojson_path


def add_attributes_to_geojson(geojson_path, fips6_dict):

	result_list = []

	with open(geojson_path, 'r') as geojson_file:
		data = json.load(geojson_file)

		for feature in data['features']:

			feature_fips = feature['properties']['FIPS6']
			feature_town = feature['properties']['TOWNNAME'].title()

			# Format it like this to make it friendlier for javascript
			# Harder in javascript to grab keys and values-- much easier to call obj.word and obj.count
			word_count_result_list = [{'word': x.keys()[0], 'count': x.values()[0]} for x in fips6_dict[feature_fips]]
			
			# Determine if there's a tie in the top counts for the top two words
			top_two_results = word_count_result_list[0:2]
			top_two_counts = [d['count'] for d in top_two_results]

			if len(set(top_two_counts)) == 1:
				final_result = 'Tie'
			else:
				final_result = word_count_result_list[0]['word']

			result_list.append(final_result)

			# Overwrite properties
			feature['properties'] = {'word_count': word_count_result_list, 'town': feature_town, 
									 'result': final_result, 'fips6': feature_fips}

	with open(geojson_path, 'w') as outfile:
		json.dump(data, outfile)

	print 'Final results: '
	print Counter(result_list)

	# To test
	cmd = ['cat data/town_boundaries.geojson | simplify-geojson -t 0.01 | geojsonio']
	subprocess.check_call(cmd, shell=True)


def tabluate_result_by_FIPS():
	fips6_dict = {}

	lookup_sql =  'SELECT fips6, town, word, count(word) as count ' \
			  	  'FROM words_by_town ' \
			      'GROUP BY town, word ' \
			      'ORDER BY town, count DESC '
					  
	lookup_rows = c.execute(lookup_sql).fetchall()

	# Build dictionary with list of dictionaries to store the top five words by town, i.e.
	# {<fips6>: [{hill: 23}, {main: 10}, ...]}
	for row in lookup_rows:
		fips6 = row[0]
		word = row[2]
		word_count = row[3]

		try:
			# Check how many words we've currently stored for this town
			num_words_associated = len(fips6_dict[fips6])

			# If it's less than 5, add it to the list
			if num_words_associated < 5:
				fips6_dict[fips6].append({word: word_count})

		# If we don't have this town in the dict yet, add it
		except KeyError:
			fips6_dict[fips6] = [{word: word_count}]

	# Add Warners Grant and Glastenbury FIPS: no valid road names
	fips6_dict[9090] = [{'None': 0}]
	fips6_dict[3018] = [{'None': 0}]

	return fips6_dict



def to_topojson():

	cmd = ['topojson', '-o', 'output.json', '-p', '--simplify-proportion', '.2', 
		   '--id-property=FIPS6', 'data/town_boundaries.geojson']
	
	subprocess.check_call(cmd)


if __name__ == '__main__':
	geojson_path = shape_to_geojson()

	fips6_dict = tabluate_result_by_FIPS()

	add_attributes_to_geojson(geojson_path, fips6_dict)

	to_topojson()