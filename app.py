from flask import Flask, redirect, render_template
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import requests 
import json

app = Flask(__name__)
# api-endpoint 
data_url = "https://api.covid19india.org/data.json"
r = requests.get(url=data_url)
jd = r.json()
resources_url = "https://api.covid19india.org/resources/resources.json"
res = requests.get(url=resources_url)
keys = set()
testing = list()
fundraisers = list()
hospitals = list()
helpline = list()
seniorSupport = list() # len = 8
police = list() # len = 100
for k in res.json()['resources']:
	keys.add(k['category'])
	if k['category'] == 'CoVID-19 Testing Lab': testing.append(k)
	if k['category'] == 'Fundraisers': fundraisers.append(k)
	if k['category'] == 'Hospitals and centers': hospitals.append(k)
	if k['category'] == 'Government Helpline': helpline.append(k)
	if k['category'] == 'Senior Citizen Support': seniorSupport.append(k)
	if k['category'] == 'Police': police.append(k)

print(keys)
# print(police)
# print(len(fundraisers))
# print(len(hospitals))

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

@app.route("/")
def home():
	return render_template('index.html', logged_in=False, data=json.dumps(df), tc=df['totalconfirmed'][-1], tr=df['totalrecovered'][-1], td=df['totaldeceased'][-1], dc=df['dailyconfirmed'][-1],dr=df['dailyrecovered'][-1],dd=df['dailydeceased'][-1])

@app.route("/testing-lab")
def testing():
	return render_template('testing.html')
    
if __name__ == "__main__":
    app.run(debug=True)