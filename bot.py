import os
import time
from slack import WebClient
import requests 
from bs4 import BeautifulSoup
import csv
from dotenv import load_dotenv
load_dotenv()
from apscheduler.schedulers import BlockingScheduler

# Request to get content of given url
page = requests.get('https://www.mohfw.gov.in/')
soup = BeautifulSoup(page.content, 'html5lib')

table = soup.findAll('div', attrs = {'class':'table-responsive'})
tr = table[0].find('tbody').findAll('tr')

cases = []
for i in range(len(tr)):
	tr[i] = tr[i].findAll('td')
	data = []
	for row in tr[i]:
		data.append(row.text.strip())
	cases.append(data)

i = len(cases)-1
while i>=0:
	if 'Total' in cases[i][0]:
		break
	i-=1

# Remove rows that are not having any info so remove it #
cases = cases[:i+1]
total = int(cases[-1][1][:-1])
cured = int(cases[-1][2])
deaths = int(cases[-1][3])
cases = cases[:-1]
data = []

for element in cases:
	case = {}
	case['STATE/UT'] = element[1]
	case['Positive'] = element[2]
	case['Cured'] = element[3]
	case['Deaths'] = element[4]
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

# post a file on the channel from the bot with specified file
def send_file(file, title):
	return client.files_upload(
			channels=os.getenv('CHANNEL_NAME'), 
			file=file,
			title=title
		)

# Setup a cronJob to send data at regular intervals
def cronJob():
	message = "Total number of confirmed cases: {}\n Total number of recovered cases: {}\n Total number deceased cases: {}".format(str(total),str(cured),str(deaths))
	response = send_message(message)
	assert response["ok"]
	response = send_file("old.csv", "New Updated Records")
	assert response["ok"]

# BlockingScheduler that will run daemon thread in background...
scheduler = BlockingScheduler()
scheduler.add_job(cronJob, 'interval', hours=3)
scheduler.start()

try:
    while True:
        time.sleep(2)
except(KeyboardInterrupt, SystemExit):
    scheduler.shutdown()