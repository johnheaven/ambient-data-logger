# ambient-data-logger
Pulls in data from an API (e.g. [Raspberry Pico with ambient data sensors](https://github.com/johnheaven/pico-ambient-data-api/tree/main)) and adds them to a CSV, recording which room, Pico and sensor type the data originated from.

It's designed to be run with a cron job, so doesn't do any timing.

My current set-up is a Raspberry Pico that exposes a simple API on the local network. This has information about ambient data (temperature, pressure, humidity). It also contains an ID and a UUID. The UUID is useful for specifying individual settings for different Picos, e.g. the name of the room and – if they have different sensor types - the type of sensor.

## Pico discovery hack

The problem is that the Pico can't set a hostname, and my router doesn't allow me to allocate a fixed IP without turning off DHCP entirely. So the logger starts with a particular IP and then searches until it finds the right IP (i.e. it can access the JSON data and it checks that the ID is the one it's looking for). Then it logs the data to CSV. It caches the best IP to a file, so it can look that up next time.

## Multiple Picos

You might have several Picos collecting data in different rooms or places. Currently, it saves .

## Setup

You need to copy the `example-settings.py` file to `settings.py` and enter the Pico IDs you want to search for. You'll need the UUID of your Pico as a string.
