from flask import Flask, redirect, render_template
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import requests 
import json
import os
import csv
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
# api-endpoint 
data_url = "https://api.covid19india.org/data.json"
r = requests.get(url=data_url)
jd = r.json()
resources_url = "https://api.covid19india.org/resources/resources.json"
res = requests.get(url=resources_url)
api_key = os.getenv("GEOCODING_KEY") # for getting api key of places API
keys = set()
test = list()
fundraisers = list() # len = 57
hospitals = list() # len = 27
helpline = list() # len = 283
seniorSupport = list() # len = 8
police = list() # len = 100

for k in res.json()['resources']:
	keys.add(k['category'])
	if k['category'] == 'CoVID-19 Testing Lab': test.append(k)
	if k['category'] == 'Fundraisers': fundraisers.append(k)
	if k['category'] == 'Hospitals and centers': hospitals.append(k)
	if k['category'] == 'Government Helpline': helpline.append(k)
	if k['category'] == 'Senior Citizen Support': seniorSupport.append(k)
	if k['category'] == 'Police': police.append(k)

print(keys)
print(police[0])
# print(fundraisers)
# print(len(hospitals))
# print(len(helpline))
# print(seniorSupport)

df = {}
now = datetime.now()
month_map = {'January':'01',
			'February':'02',
			'March':'03',
			'April':'04',
			'May':'05', 
			'June':'06',
			'July':'07',
			'August':'08',
			'September':'09',
			'October':'10',
			'November':'11',
			'December':'12'}

year = str(now.year)
json_data = jd['cases_time_series']
for i in range(len(json_data)):
	for key in json_data[i]:
		if key not in df:
			df[key] = []
		if key == 'date':
			date = json_data[i][key].split(' ')
			df[key].append(year+'-'+month_map[date[1]]+'-'+date[0])
		else: df[key].append(json_data[i][key])

def geocode(data_list, filename):
	print("Called geocode")
	coords = []
	for i in range(len(data_list)):
		place = data_list[i]['city']+','+data_list[i]['state']
		r = requests.get(url='https://api.opencagedata.com/geocode/v1/geojson?q={}&key={}'.format(place,api_key))
		pos = r.json()['features'][0]['geometry']['coordinates']
		print(pos)
		coords.append({'lat': pos[1], 'lng': pos[0]})

	with open(filename, 'w') as f: 
	    w = csv.DictWriter(f,['lat','lng'])
	    w.writeheader() 
	    for data in coords: 
	    	w.writerow(data)

def testJSONData():
	testing_data = []
	coords_df = pd.read_csv('testing_coords.csv')
	for i in range(len(coords_df)):
		c = {}
		c['phone'] = test[i]['phonenumber'].split(',')[0]
		c['link'] = test[i]['contact']
		c['name'] = test[i]['nameoftheorganisation']
		c['lat'] = coords_df['lat'][i]
		c['lng'] = coords_df['lng'][i]
		testing_data.append(c)
	 # Writing to testing_data.json
	json_object = json.dumps(coords, indent=4)
	with open("testing_data.json", "w") as f: 
	    f.write(json_object)

def policeJSONData():
	police_data = []
	coords_df = pd.read_csv('police_coords.csv')
	for i in range(len(police)):
		p = {}
		p['name'] = police[i]['nameoftheorganisation']
		p['descr'] = police[i]['descriptionandorserviceprovided']
		p['phone'] = police[i]['phonenumber'].split(' ')[0]
		p['contact'] = police[i]['contact']
		p['lat'] = coords_df['lat'][i]
		p['lng'] = coords_df['lng'][i]
		police_data.append(p)
	 # Writing to testing_data.json
	json_object = json.dumps(police_data, indent=4)
	with open("police_data.json", "w") as f: 
	    f.write(json_object)


@app.route("/")
def home():
	return render_template('index.html', data=json.dumps(df), tc=df['totalconfirmed'][-1], tr=df['totalrecovered'][-1], td=df['totaldeceased'][-1], dc=df['dailyconfirmed'][-1],dr=df['dailyrecovered'][-1],dd=df['dailydeceased'][-1])

@app.route("/testing-lab")
def testing():
	# geocode(test,'testing_coords.csv')
	# testJSONData()
	f = open('testing_data.json', 'r')
	data = json.load(f)
	return render_template('testing.html', data=data)

@app.route("/police")
def policeHelp():
	# geocode(police,'police_coords.csv')
	# policeJSONData()
	f = open('police_data.json', 'r')
	data = json.load(f)
	return render_template('police.html', data=data)
    
if __name__ == "__main__":
    app.run(debug=True)