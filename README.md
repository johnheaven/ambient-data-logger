# ambient-data-logger
Pulls in data from an API (e.g. Raspberry Pico with ambient data sensors) and adds them to a CSV.

It's designed to be run with a cron job, so doesn't do any timing.

My current set-up is a Raspberry Pico that exposes a simple API on the local network. This has information about ambient data (temperature, pressure, humidity). It also contains an ID.

The problem is that the Pico can't set a hostname, and my router doesn't allow me to allocate a fixed IP without turning off DHCP entirely. So the logger starts with a particular IP and then searches until it finds the right IP (i.e. it can access the JSON data and it checks that the ID is the one it's looking for). Then it logs the data to CSV.
