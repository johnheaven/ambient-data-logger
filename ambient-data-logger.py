import requests
import time
import csv

sensor_id = 1

### GET DATA

# Get a random number from random.org API
API_attempts = 0
http_response = None

# Try 5 times to get a reading
while http_response != 200:
    response = requests.get(url='http://192.168.2.135/data/', timeout=2)
    http_response = response.status_code
    print ('HTTP response: ', http_response)
    # 200 means success
    if http_response == 200:
        ambient_data = response.json()
        break

    API_attempts += 1
    time.sleep(2)

ambient_data.insert(0, time.asctime(time.localtime()))

### WRITE TO CSV
# assuming headers are already present

with open(f"{sensor_id}_ambient_data.csv", mode='a', newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(ambient_data)
