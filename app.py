from flask import Flask, redirect, render_template
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from flask_moment import Moment
import requests 
import json

# api-endpoint 
URL = "https://api.covid19india.org/data.json"
r = requests.get(url = URL) 
jd = r.json()
app = Flask(__name__)
moment = Moment(app)
df = {}
now = datetime.now()
month_map = {'January':'01',
			'February':'02',
			'March':'03',
			'April':'04',
			'May':'05', 
			'June':'06',
			'July':'07'}

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

# filename = 'case_time_series.csv'
# df = pd.read_csv(filename, header=0)
# data = pd.DataFrame()
# dates = []
# for d in df['Date']:
# 	date = d.split(' ')
# 	date_str = year+'-'+month_map[date[1]]+'-'+date[0]
# 	# dates.append(datetime.strptime(date_str, '%d-%m-%Y').date())
# 	dates.append(date_str)
# data['Date'] = pd.Series(dates)
# keys = list(df.keys())[1:]
# data[keys] = df[keys]
# print(data)

@app.route("/")
def home():
	return render_template('index.html', logged_in=False, data=json.dumps(df))
    
if __name__ == "__main__":
    app.run(debug=True)