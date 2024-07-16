import requests, json
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
	#print("Distance between cities: " + str(d) + '\n')
	return d
	
#Pre: both arguments are strings and country follows the ISO_A2 encoding.
#Post: if the location is found returns a dictionary with its coordinated points, otherwise returns a dictionary of None values.
	#If more than one location is found it returns the coordinated points of the first location given by the api.
def reverse_geocode(country, city, apikey):
	#Preparing the get request
	url = "https://geocode.maps.co/search?city=" + city + "&state=" + country + "&api_key=" + apikey
	sleep(1)#with the free plan of the api you just can make a request per second, this line is added for prevention reasons
	#Sending the request and getting the json object
	response = requests.get(url)
	location = response.json()
	response.close()
	
	#Parsing the first json object
	lon = None
	lat = None
	
	if len(location) == 0 or not "lon" in location[0] or not "lat" in location[0]:
		return {"lon":lon, "lat":lat}
		
	lon = location[0]["lon"]
	lat = location[0]["lat"]
		
	#print(country + ", " + city + " --> " + lon + ", " + lat)
	return {"lon":float(lon), "lat":float(lat)}

#Pre: path is a valid path defining an excel file. Sheet is a valid sheet name of the given path.
#Post: retrurn the excel sheet as a pandas dataFrame.
def get_cities_from_excel(path = "Ciutats a informar.xlsx", sheet = "Hoja1"):
	return pd.read_excel(path, sheet_name = sheet)

#Pre: path is a valid path defining an excel file. Sheet is a valid sheet name.
#Post: the dataFrame df is saved in the excel file given in the given sheet name. If not exists it creates one. 
def save_cities_to_excel(df, path, sheet = "Ciutats informades"):
	df.to_excel(path, sheet_name = sheet, float_format="%.2f")

#It is assumed that the excel is formed by four columns
#[COUNTRY ISO_A ENCODING, COUNTRY ISO_A2 ENCODING, COUNTRY PRIVATE ENCODING, CITY NAME, DISTANCE]
cities_to_inform_df = get_cities_from_excel()

cities_not_found = []

apikey = input("Please, provide the api key: ") 
origin = reverse_geocode("ES", "Barcelona", apikey)

for i in range(len(cities_to_inform_df.index)):
	cities_to_inform_df.iat[i, 4] = None
	j = 0
	#Trying every country encoding until one matches or there are no enconding left
	while pd.isnull(cities_to_inform_df.iat[i, 4]) and j in range(3):
		#print(str(j) + ", " + cities_to_inform_df.iat[i, j] + " " + cities_to_inform_df.iat[i, 3])
		destiny = reverse_geocode(cities_to_inform_df.iat[i, j], cities_to_inform_df.iat[i, 3], apikey)
		if not (destiny.get("lon") is None):
			cities_to_inform_df.iat[i, 4] = haversine_distance(origin.get("lon"), origin.get("lat"), destiny.get("lon"), destiny.get("lat"))
		j = j + 1
	if pd.isnull(cities_to_inform_df.iat[i, 4]):
		cities_not_found.append({"country" : cities_to_inform_df.iat[i, 0], "city" : cities_to_inform_df.iat[i, 3]})
	if ( i % 25 == 0):
		print("Calculated " + str(i) + " distances") #Feedback for the user

save_cities_to_excel(cities_to_inform_df, "Ciutats informades - " + strftime("%Y_%m_%d %H_%M_%S", localtime()) +  ".xlsx")

print(cities_not_found)

input()