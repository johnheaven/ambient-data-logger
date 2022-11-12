import requests
import time
import csv
import json

from ip_search.ip_search import ip_search
from settings import sensor_ids

all_ambient_data = []

for sensor_id in sensor_ids:
# last 3 digits of IP address so we can find the right one by trial and error
    try:
        previous_best = json.load(open(f'cache/best-ip-cache__{sensor_id}.json', 'r'))
    except FileNotFoundError as e:
        print(e)
        starting_ip_last_3 = 145
    else:
        starting_ip_last_3 = previous_best

    ips = ip_search(starting_ip_last_3=starting_ip_last_3, max_steps=10)

    ### GET DATA

    success = False

    # run a loop until we get success or we run out of IPs to try
    while (not success) and (ips.get_uri()):
        try:
            pico_url = ips.get_uri()
            print(f'Trying URL {pico_url}')
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
                print(f'Couldn\'t find device with sensor ID {sensor_id}')


    ambient_data['time'] = time.asctime(time.localtime())
    print(ambient_data)

    ### WRITE IP TO JSON FOR NEXT TIME
    sensor_id_clean = sensor_id.replace(' ', '_')
    json.dump(ips.get_current(), open(f'cache/best-ip-cache__{ sensor_id_clean }.json', 'w'))

    all_ambient_data.append(ambient_data)

    ### WRITE TO CSV

# assuming headers are already present
with open(f'data/ambient_data.csv', mode='a', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=('time', 'temp', 'pressure', 'humidity', 'sensor', 'pico_id', 'pico_uuid'))
    for ambient_data in all_ambient_data:
        writer.writerow(ambient_data)
