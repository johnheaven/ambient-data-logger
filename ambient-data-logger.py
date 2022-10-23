import requests
import time
import csv

from ip_search import ip_search

sensor_id = '1'
# last 3 digits of IP address so we can find the right one by trial and error
starting_ip_last_3 = 135

ips = ip_search(current_ip_last_3=142, ip_min=130, ip_max=200)

### GET DATA

success = False

# run a loop until we get success or we run out of IPs to try
while (not success) and (ips.get_ip()):
    try:
        pico_url = ips.get_ip()
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
            ambient_data = response.json()
            # check whether it's from the right Pico (for the case that there are several)
            if ambient_data['pico_id'] == sensor_id:
                success = True
    # bump the IP up one so we can try it next
    ips.bump_sensor_ip()
    if not ips.get_ip():
        print('Couldn\'t find device with sensor ID %s' % sensor_id)


ambient_data['time'] = time.asctime(time.localtime())
print(ambient_data)
### WRITE TO CSV

# assuming headers are already present
with open('%s_ambient_data.csv' % sensor_id, mode='a', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=('time', 'temp', 'pressure', 'humidity', 'sensor', 'pico_id'))
    writer.writerow(ambient_data)
