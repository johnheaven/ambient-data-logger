import requests
import time
import csv
import json
from os import environ

from ip_search import ip_search

sensor_id = '1'

# last 3 digits of IP address so we can find the right one by trial and error
try:
    previous_best = json.load(open('best-ip-cache.json', 'r'))
except FileNotFoundError as e:
    print(e)
    starting_ip_last_3 = 145
else:
    starting_ip_last_3 = previous_best

ips = ip_search(starting_ip_last_3=starting_ip_last_3, max_steps=50)

### GET DATA

success = False

# run a loop until we get success or we run out of IPs to try
while (not success) and (ips.get_uri()):
    try:
        pico_url = ips.get_uri()
        print('Trying URL %s' % pico_url)
        response = requests.get(url=pico_url, timeout=5)
    except:
        print('Connection attempt failed.')
    else:
        # get the response code
        http_response = response.status_code
        print ('HTTP response: ', http_response)
        # 200 means success
        if http_response == 200:
            # get data from JSON
            try:
                ambient_data = response.json()
            except ValueError as e:
                print(e)
            else:
                # check whether it's from the right Pico (for the case that there are several)
                if ambient_data['pico_id'] == sensor_id:
                    success = True
    # bump the IP up one so we can try it next.
    # don't do this if success==True so we can preserve the right value for storing in env var later
    if not success:
        ips.bump_sensor_ip()
        if not ips.get_uri():
            print('Couldn\'t find device with sensor ID %s' % sensor_id)


ambient_data['time'] = time.asctime(time.localtime())
print(ambient_data)

### WRITE IP TO JSON FOR NEXT TIME
json.dump(ips.get_current(), open('best-ip-cache.json', 'w'))

### WRITE TO CSV

# assuming headers are already present
with open('%s_ambient_data.csv' % sensor_id, mode='a', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=('time', 'temp', 'pressure', 'humidity', 'sensor', 'pico_id'))
    writer.writerow(ambient_data)
