import os
import time
from slack import WebClient
import requests 
from bs4 import BeautifulSoup
import csv
from dotenv import load_dotenv
load_dotenv()

URL = os.getenv('URL')
# Request to get content of given url
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html5lib')
# print(soup.prettify())
table = soup.findAll('div', attrs = {'class':'table-responsive'})
tr = table[7].find('tbody').findAll('tr')
# for i in range(len(table)):
# 	print("\t\t\t{}\n".format(str(i)))
# 	print(table[i])
# 	print("\n\n")
cases = []
for i in range(len(tr)):
	tr[i] = tr[i].findAll('td')
	data = []
	for row in tr[i]:
		data.append(row.text.strip())
	cases.append(data)

# Last Row is not having any info so remove it #
cases = cases[:-1]
total = int(cases[-1][1][:-1])+int(cases[-1][2])
cured = int(cases[-1][3])
deaths = int(cases[-1][4])
cases = cases[:-1]
data = []

for element in cases:
	case = {}
	case['STATE/UT'] = element[1]
	case['Positive'] = str(int(element[2])+int(element[3]))
	case['Cured'] = element[4]
	case['Deaths'] = element[5]
	data.append(case)

filename = 'old.csv'
with open(filename, 'w') as f: 
    w = csv.DictWriter(f,['STATE/UT','Positive','Cured','Deaths']) 
    w.writeheader() 
    for line in data: 
        w.writerow(line)

# instantiate Slack client with the slack bot token
client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'), timeout=30)

# post a message on the channel from the bot with specified text

def send_message(message):
	return client.chat_postMessage(
				channel=os.getenv('CHANNEL_NAME'), 
				text=message,
			)

def send_file(file, title):
	return client.files_upload(
			channels=os.getenv('CHANNEL_NAME'), 
			file=file,
			title=title
		)

message = "Total number of confirmed cases: {}\n Total number of recovered cases: {}\n Total number deceased cases: {}".format(str(total),str(cured),str(deaths))
response = send_message(message)
assert response["ok"]
response = send_file("old.csv", "Some data")
assert response["ok"]