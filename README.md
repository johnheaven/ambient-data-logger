# ambient-data-logger
Pulls in data from an API (e.g. [Raspberry Pico with ambient data sensors](https://github.com/johnheaven/pico-ambient-data-api/tree/main)) and adds them to a CSV, one for each sensor.

It's designed to be run with a cron job, so doesn't do any timing.

My current set-up is a Raspberry Pico that exposes a simple API on the local network. This has information about ambient data (temperature, pressure, humidity). It also contains an ID and a UUID.

## Pico discovery hack

The problem is that the Pico can't set a hostname, and my router doesn't allow me to allocate a fixed IP without turning off DHCP entirely. So the logger starts with a particular IP and then searches until it finds the right IP (i.e. it can access the JSON data and it checks that the ID is the one it's looking for). Then it logs the data to CSV. It caches the best IP to a file, so it can look that up next time.

## Multiple Picos

You might have several Picos collecting data in different rooms or places. Currently, it just saves a separate CSV for each of these as a good-enough solution.

## Setup

You need to copy the `example-settings.py` file to `settings.py` and enter the Pico IDs you want to search for (not UUIDs, although that might be a better approach in the future).

## Designed for the Raspberry Pi

I run this on my Raspberry Pi 4, which has an ancient Python 3 version installed on it (sigh). Thus, f-strings aren't supported, which is why I use the % notation.