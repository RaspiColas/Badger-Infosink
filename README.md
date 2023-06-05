Set of Python files for Pimoroni's BADGER2049w to turn it into an infomration sink:
- A set of pages (tabs) to display local weather and forecast 
- A set of pages (tabs) to display astronomical information
- A set of pages (tabs) to display local information retrieved from other local servers
Navigation between the set of pages is done via the keys "A", "B", "C" on the badger. Navigation between the tabs is done via the keys UP and DOWN

Due to memory size limitation of the Badger, each request for a set of pages drops all functions from memory and loads the new functions on-the-fly (does not work otherwise)


WEATHER:

A Python script (wethaer_badger.py) grabs weather data from openweathermap and displays them on Badger 2040 : 
- current weather condition (1st tab)
- forecast for the next 4 days (other tabs)

Requires 
- Weather images in  /wicons/
- Wind direction images in /windir/
- common_badger.py library of common functions and data
- Fill up OPENWEATHER_ID in the script


ASTRO:

A Python script (astro_badger.py) grabs astronomical data and displays them on Badger 2040 : 
- planets ephemeris 
- Moon phase
- ISS position

Fetches info from :
- Ephemeris data from IMCCE (More info: http://vo.imcce.fr/webservices/miriade/?rts#KnownBodies)
- ISS location data from open-notify.org/iss-now.json

Requires 
- Moon phase images in  /Phases/
- World map in /astricons/world_map_m.jpg
- common_badger.py library of common functions and data


LOCAL DATA:

A Python script (not included) grabs various data from local Pi and displays them on Badger 2040 : 
- CO2 level
- Strava data
- Temperature from various locations

Fetches info from :
- Local Pi measuring CO2 level
- Local Pi capturing Strava data
- Local Pi capturing temperature values for various location

Requires 
- Local Pi to grab info from
- common_badger.py library of common functions and data

