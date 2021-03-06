from flask import Flask, redirect, render_template
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
import requests 
import json
import os
import csv
import math
from dotenv import load_dotenv
from flask_moment import Moment
from difflib import SequenceMatcher
load_dotenv()

app = Flask(__name__)
moment = Moment(app)
# api-calling
r = requests.get(url=os.getenv('DATA_URL'))
jd = r.json()
res = requests.get(url=os.getenv('RESOURCES_URL'))
api_key = os.getenv('GEOCODING_KEY') # for getting api key of places API
state_data = requests.get(url=os.getenv('STATE_URL')).json()
t = requests.get(url=os.getenv('TEST_URL')).json()['states_tested_data']
zone_data = requests.get(url=os.getenv('ZONE_URL')).json()['zones']
news_data = requests.get(url=(os.getenv('NEWS_URL')+os.getenv('NEWS_API'))).json()['articles']

payload = {"key": "{}".format(os.getenv('KEY')),"lng": 73.0933867, "lat": 19.220705199999998, "radius": 1000}
headers = {
  'accept': 'application/json',
  'Content-Type': 'application/json',
  'Content-Type': 'application/json'
}

def similar(a, b):
	return SequenceMatcher(None, a, b).ratio()

state_test = dict()
maxTest = -1
state = ""
for i in range(len(t)): 
	if t[i]['totaltested'] != '':
		state_test[t[i]['state']] = int(t[i]['totaltested'])
	
for s in state_test:
	temp = max(maxTest, state_test[s])
	if maxTest != temp: state = s
	maxTest = temp

zones = dict()

for zone in zone_data:
	district = zone['district']
	if 'Other' in district : district = 'Unknown'
	statecode = zone['state']
	if statecode not in zones: 
		zones[statecode] = dict()
	zones[statecode][district] = zone['zone']	

def countDays(date1, date2): 
    return (date2-date1).days

date1 = date(2020,1,30) 
date2 = date.today()

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

# print(keys)
# print(police[0])
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
json_state_data = jd['statewise']
totaltested = jd['tested'][-1]['totalsamplestested']

for i in range(len(json_data)):
	for key in json_data[i]:
		if key not in df:
			df[key] = []
		if key == 'date':
			date = json_data[i][key].split(' ')
			df[key].append(year+'-'+month_map[date[1]]+'-'+date[0])
		else: df[key].append(json_data[i][key])

def geocode(datalist, filename):
	coords = []
	print(len(datalist))
	for i in range(len(datalist)):
		place = datalist[i]['city']+','+datalist[i]['state']
		r = requests.get(url='https://api.opencagedata.com/geocode/v1/geojson?q={}&key={}'.format(place,api_key))
		pos = r.json()['features'][0]['geometry']['coordinates']
		print(i,pos)
		coords.append({'lat': pos[1], 'lng': pos[0]})

	with open('{}_coords.csv'.format(filename), 'w') as f: 
	    w = csv.DictWriter(f,['lat','lng'])
	    w.writeheader() 
	    for data in coords: 
	    	w.writerow(data)

def testJSONData():
	testing_data = []
	coords_df = pd.read_csv('testing_coords.csv')
	for i in range(len(coords_df)):
		c = {}
		c['phone'] = test[i]['phonenumber']
		c['link'] = test[i]['contact']
		c['name'] = test[i]['nameoftheorganisation']
		c['lat'] = coords_df['lat'][i]
		c['lng'] = coords_df['lng'][i]
		testing_data.append(c)
	 # Writing to testing_data.json
	json_object = json.dumps(coords, indent=4)
	with open("testing_data.json", "w") as f: 
	    f.write(json_object)

def makeJSONData(datalist, filename):
	data = []
	coords_df = pd.read_csv('{}_coords.csv'.format(filename))
	for i in range(len(datalist)):
		d = {}
		d['name'] = datalist[i]['nameoftheorganisation']
		d['descr'] = datalist[i]['descriptionandorserviceprovided']
		d['phone'] = datalist[i]['phonenumber']
		d['contact'] = datalist[i]['contact']
		d['lat'] = coords_df['lat'][i]
		d['lng'] = coords_df['lng'][i]
		data.append(d)
	 # Writing to {filename}.json
	jsonObject = json.dumps(data, indent=4)
	with open("{}_data.json".format(filename), "w") as f: 
	    f.write(jsonObject)

@app.route("/")
def home():
	_ci=math.ceil(100*(int(df['dailyconfirmed'][-1])/int(df['totalconfirmed'][-1])))
	_ri=math.ceil(100*(int(df['dailyrecovered'][-1])/int(df['totalrecovered'][-1])))
	_di=math.ceil(100*(int(df['dailydeceased'][-1])/int(df['totaldeceased'][-1])))
	return render_template('index.html', data=json.dumps(df), tc=df['totalconfirmed'][-1], tr=df['totalrecovered'][-1], td=df['totaldeceased'][-1], dc=df['dailyconfirmed'][-1],dr=df['dailyrecovered'][-1],dd=df['dailydeceased'][-1], _ci=_ci, _ri=_ri, _di=_di, days=countDays(date1, date2), state=state_data, totaltested=totaltested, maxState=state, maxTests=maxTest, state_test=json.dumps(state_test), zones=json.dumps(zones))

@app.route("/testing-lab")
def testing():
	# geocode(test,'testing_coords.csv')
	# testJSONData()
	f = open('testing_data.json', 'r')
	data = json.load(f)
	return render_template('testing.html', data=data)

@app.route("/police")
def policeHelp():
	# geocode(police, 'police')
	# makeJSONData(police, 'police')
	f = open('police_data.json', 'r')
	data = json.load(f)
	return render_template('police.html', data=data)

@app.route("/helpline")
def helplineNumbers():
	# geocode(helpline, 'helpline')
	# makeJSONData(helpline, 'helpline')
	f = open('helpline_data.json', 'r')
	data = json.load(f)
	return render_template('helpline.html', data=json.dumps(data))

@app.route("/donate")
def donate():
	# geocode(fundraisers, 'donate')
	# makeJSONData(fundraisers, 'donate')
	f = open('donate_data.json', 'r')
	data = json.load(f)
	return render_template('donate.html', data=json.dumps(data))
    
@app.route("/map")
def map():
	return render_template('map.html', data=json_state_data)

@app.route("/news")
def news():
	return render_template('news.html', news=news_data)

if __name__ == "__main__":
    app.run(debug=True)