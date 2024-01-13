import requests
import time
import csv

from sqlalchemy.schema import Table, MetaData

from helpers.ip_search import ip_search
from settings import sensor_ids
from sqldb.sqldb import get_sql_engine

all_ambient_data = []

ip_list = None

for sensor_id in sensor_ids:
    sensor_id_clean = sensor_id.replace(' ', '_')

    ips = ip_search(sensor_id=sensor_id_clean, max_steps=100, ip_list=ip_list)

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
                finally:
                    response.close()
        # bump the IP up one so we can try it next.
        # don't do this if success==True so we can preserve the right value for storing in env var later
        if not success:
            ips.bump_sensor_ip()
            if not ips.get_uri():
                print(f'Couldn\'t find device with sensor ID {sensor_id}')

    if success:
        ambient_data['time'] = time.asctime(time.localtime())
        print(ambient_data)

        ### WRITE IP TO JSON FOR NEXT TIME
        ips.write_cache()

        all_ambient_data.append(ambient_data)

        ip_list = ips.get_untried_ips()

### WRITE TO CSV

# assuming headers are already present
fieldnames = ('time', 'temp', 'pressure', 'humidity', 'sensor', 'pico_id', 'pico_uuid')
with open(f'data/ambient_data.csv', mode='a', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    for ambient_data in all_ambient_data:
        writer.writerow(ambient_data)

### WRITE TO SQL
engine = get_sql_engine()

ambient_data_table = Table('ambient_data', MetaData(), autoload_with=engine)

with engine.connect() as conn:
    # see example: https://stackoverflow.com/questions/64090818/unconsumed-column-names-sqlalchemy-python
    for ambient_data in all_ambient_data:
        conn.execute(
            ambient_data_table.insert().values(ambient_data)
        )
