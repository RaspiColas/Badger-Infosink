# Badger-Infosink

Project description:
- [En]: https://raspicolas.wordpress.com/2023/06/07/turning-a-raspberry-pico-into-an-infosink-display/
- [Fr]: https://www.framboise314.fr/comment-transformer-un-raspberry-pico-en-centrale-dinformation-pour-sa-cuisine/

Set of Python files for Pimoroni's BADGER2040w to turn it into an information sink and display 3 sets of pages:
- A set of pages (tabs) to display local weather and forecast 
- A set of pages (tabs) to display astronomical information
- A set of pages (tabs) to display local information retrieved from other local servers

Navigation between the set of pages is done via the keys "A", "B", "C" on the badger. 
Navigation between the tabs is done via the keys UP and DOWN

Notes:
- Due to memory size limitation of the Badger, each request for a set of pages drops all functions from memory and loads the new functions on-the-fly (does not work otherwise)
- Set the LAT, LONG, LOCATION, COUNTRY and TIMEZONE (For Europe's daylight saving time: 1 for wintertime, 2 for summertime) in common_badger.py
- Info is displayed in French if COUNTRY == 'Fr', otherwise in English
- First pages to be displayed is Astro. To be changed in the main.py if another page should be displayed at boot time


WEATHER:

A Python script (wethaer_badger.py) grabs weather data from openweathermap and displays them on Badger 2040 : 
- current weather condition (1st tab)
- forecast for the next 4 days (other tabs)

Requires 
- Weather images in  /wicons/
- Wind direction images in /windir/
- common_badger.py library of common functions and data
- Fill up OPENWEATHER_ID in the script
- Set LAT, LONG, LOCATION, COUNTRY and TIMEZONE in common_badger.py


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

