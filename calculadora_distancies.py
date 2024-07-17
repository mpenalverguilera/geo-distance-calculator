import requests, json, configparser, sys
import pandas as pd
from math import sqrt, sin, cos, asin
from time import localtime, strftime, sleep

#Pre: degree is a float or can be casted to a float.
#Post: returns the radian representation of degree.
def degrees_to_radians(degree):
	return float(degree)*0.01745329251

#Pre: all the paramaters are floats or can be casted to floats.
#Post: returns the haversine distance in kilometers between the coordinated points supposing the earth is an sphere.
	#Haversine distance is the minimum distance between two points in a sphere.
def haversine_distance(lon1, lat1, lon2, lat2):
	radius = 6371.0710	#Radius of earth in km
	diff_lon = degrees_to_radians(lon1-lon2)
	diff_lat = degrees_to_radians(lat1-lat2)
	rlat1 = degrees_to_radians(lat1)
	rlat2 = degrees_to_radians(lat2)
	
	d = 2 * radius * asin(sqrt( sin(diff_lat/2)*sin(diff_lat/2) + cos(rlat1)*cos(rlat2)*sin(diff_lon/2)*sin(diff_lon/2)))
	#print('Distance between cities: ' + str(d) + '\n')
	return d
	
#Pre: both arguments are strings and country follows the ISO_A2 encoding.
#Post: if the location is found returns a dictionary with its coordinated points, otherwise returns a dictionary of None values.
	#If more than one location is found it returns the coordinated points of the first location given by the api.
def reverse_geocode(country, city, apikey):
	#Preparing the get request
	url = 'https://geocode.maps.co/search'
	sleep(1)#with the free plan of the api you just can make a request per second, this line is added for prevention reasons
	#Sending the request and getting the json object
	try:
		response = requests.get(url, params = {'city': city, 'state': country, 'api_key': apikey})
	except requests.exceptions.RequestException as e:
		raise SystemExit(e)
		
	location = response.json()
	response.close()
	
	#Parsing the first json object
	lon = None
	lat = None
	
	if len(location) == 0 or not 'lon' in location[0] or not 'lat' in location[0]:
		return {'lon':lon, 'lat':lat}
		
	lon = location[0]['lon']
	lat = location[0]['lat']
		
	#print(country + ', ' + city + ' --> ' + lon + ', ' + lat)
	return {'lon':float(lon), 'lat':float(lat)}

#Pre: path is a valid path defining an excel file. Sheet is a valid sheet name of the given path.
#Post: retrurn the excel sheet as a pandas dataFrame.
def get_cities_from_excel(path, sheet):
	return pd.read_excel(path, sheet_name = sheet)

#Pre: path is a valid path defining an excel file. Sheet is a valid sheet name.
#Post: the dataFrame df is saved in the excel file given in the given sheet name. If not exists it creates one. 
def save_cities_to_excel(df, path, sheet):
	df.to_excel(path, sheet_name = sheet, float_format='%.2f')

#Pre: true
#Post: creates or overwrites the configuration file of this program in the process working directory
def create_config():
	config = configparser.ConfigParser()
	
	config['general'] = {'api_key': ''}
	config['input_excel'] = {'path': 'Ciutats a informar.xlsx', 'sheet_name': 'Hoja1'}
	config['output_excel'] = {'run_time_path': True , 'path': 'Ciutats informades.xlsx', 'sheet_name': 'Hoja1'}
	config['origin'] = {'country': 'ES', 'city':'Barcelona'}
	
	# Write the configuration to a file
	config.write(open('config.ini', 'w'))
		
#Pre: exists a file named config.ini in the process working directory
#Post: return a dictionary with the values of the configuration file
def read_config():
	config = configparser.ConfigParser()

    # Read the configuration file
	config.read('config.ini')
	
	# Access values from the configuration file
	api_key = config.get('general', 'api_key')
	input_path = config.get('input_excel', 'path')
	input_sheet_name = config.get('input_excel', 'sheet_name')
	output_run_time_path = config.getboolean('output_excel', 'run_time_path')
	
	if output_run_time_path:
		output_path = str('Ciutats informades - ' + strftime('%Y_%m_%d %H_%M_%S', localtime()) +  '.xlsx')
	else:
		output_path = config.get('output_excel', 'path')
		
	output_sheet_name = config.get('output_excel', 'sheet_name')
	origin_country = config.get('origin', 'country')
	origin_city = config.get('origin', 'city')
	
	# Return a dictionary with the retrieved values
	config_values = {
		'api_key' : api_key,
		'input_path' : input_path,
		'input_sheet_name' : input_sheet_name,
		'output_path' : output_path,
		'output_sheet_name' : output_sheet_name,
		'origin_country' : origin_country,
		'origin_city' : origin_city
	}
	
	return config_values
	
	
#Pre: 0 <= i <= total
#Post: terminal updated
def update_waiting_bar(i, total):
	bar_length = 50
	completed = int(round(bar_length*(float(i)/float(total))))
	percentage = round((float(i)/float(total))*100, 1)
	bar = '=' * completed + '-' * (bar_length - completed)
	sys.stdout.write('Calculated %s of %s [%s] %s%\r' %(str(i), str(total), bar, percentage))

	if (i == total):
		print('\n')

if __name__ == "__main__":
	config_values = None
	#Checking if the config file exists if not it creates it
	try:
		config_values = read_config()
	except:
		create_config()
		config_values = read_config()

	cities_to_inform_df = get_cities_from_excel(config_values['input_path'], config_values['input_sheet_name'])
	cities_not_found = []

	apikey = config_values['api_key']
	origin = reverse_geocode(config_values['origin_country'], config_values['origin_city'], apikey)

	
	if origin.get('lon') is None:
		print('Origin city not found\nExiting...')
		exit()

	for i in range(len(cities_to_inform_df.index)):
		cities_to_inform_df.iat[i, 4] = None
		j = 0
		#Trying every country encoding until one matches or there are no enconding left
		while pd.isnull(cities_to_inform_df.iat[i, 4]) and j in range(3):
			#print(str(j) + ', ' + cities_to_inform_df.iat[i, j] + ' ' + cities_to_inform_df.iat[i, 3])
			destiny = reverse_geocode(cities_to_inform_df.iat[i, j], cities_to_inform_df.iat[i, 3], apikey)
			if not (destiny.get('lon') is None):
				cities_to_inform_df.iat[i, 4] = haversine_distance(origin.get('lon'), origin.get('lat'), destiny.get('lon'), destiny.get('lat'))
			j += 1
		if pd.isnull(cities_to_inform_df.iat[i, 4]):
			cities_not_found.append({'country' : cities_to_inform_df.iat[i, 0], 'city' : cities_to_inform_df.iat[i, 3]})
		update_waiting_bar(i + 1, len(cities_to_inform_df.index))

	save_cities_to_excel(cities_to_inform_df, config_values['output_path'], config_values['output_sheet_name'])

	print("Not founded cities:")
	print(cities_not_found)
