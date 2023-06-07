#!/usr/bin/python
# -*- coding: utf-8 -*-

#---------------------------------------------------#
#                                                   #
#                astro_badger.py                    #
#                by N.MERCOUROFF, 2023              #
#                                                   #
#---------------------------------------------------#

"""
Python script to grab astronomical data and displays them on Badger 2040 : 
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
- Set LAT, LONG, LOCATION, COUNTRY and TIMEZONE in common_badger.py

"""

import badger2040w as badger2040
import urequests
import jpegdec
from time import localtime, sleep
from ntptime import settime

from common_badger import *

VERBOSE = True

EPHEM_URL = "https://vo.imcce.fr/webservices/miriade/rts_query.php?-mime=text&-ep=%s&-body=1,2,4,5,6,10,11&-long=%s&-lat=%s"
MOON_URL = "https://vo.imcce.fr/webservices/miriade/ephemcc_query.php?-mime=json&-ep=%s-%s&-name=s:moon"

ISS_URL = 'http://api.open-notify.org/iss-now.json'
ISS_MAP = "/astricons/world_map_m.jpg"
MOONDIR = '/phases/'

current = {}

if COUNTRY == 'Fr':
    TAB_NAMES = ["Ephemérides", "ISS", "Lune"]
    dirs_cr = ['PL', 'gp', 'pq', 'ppq', 'NL']
    dirs_dc = ['PL', 'gd', 'dq', 'ddq', 'NL']

else:
    TAB_NAMES = ["Ephemeris", "ISS", "Moon"]
    dirs_cr = ['full', 'GF', 'FQ', 'FFQ', 'new']
    dirs_dc = ['full', 'GL', 'LQ', 'LLQ', 'new']

jpg_cr = ['full', 'gp', 'pq', 'ppq', 'new']
jpg_dc = ['full', 'gd', 'dq', 'ddq', 'new']

body_list = ["Sun", "Moon", "Venus", "Mars", "Jupiter", "Saturn"]
body_list_fr = {
    "Sun": "Soleil",
    "Moon": "Lune",
    "Mercury": "Mercure",
    "Venus": "Venus",
    "Mars": "Mars",
    "Jupiter": "Jupiter",
    "Saturn": "Saturne"
}

TAB_NB = len(TAB_NAMES)
tab = 1 # Let's start with "ISS" tab !

# Display Setup

display = badger2040.Badger2040W()
display.set_update_speed(2)

jpeg = jpegdec.JPEG(display.display)


#-------------------------------------------------
#		Astro functions
#-------------------------------------------------

def currenttime():
    '''Retrieves current time and stores it in current'''
    
    global current

    for i in range(TRY_NB):
        try:
            settime()
            break
        except:
            print_debug("Attempt %s to connect" % (i))
            display.connect()
        
    dt = localtime()
    date_ymd = "%s-%s-%s" % (dt[0], dt[1], dt[2])
    date_dm = "%s/%s" % (dt[2], dt[1])
    time_hm = '{:02d}:{:02d}'.format((dt[3]+TIMEZONE)%24, dt[4])
    wd = WEEKDAYS[dt[6]]
    current = {
        "date_ymd": date_ymd,
        "date_dm": date_dm,
        "time_hm": time_hm,
        "wd": wd
    }
    return


def hm_local_convert(hm):
    '''Converts UT string into local time string'''
    
    hm_split = hm.split(':')
    try:
        h = (int(hm_split[0]) + TIMEZONE) % 24
        m = int(hm_split[1])
    except:
        h = 0
        m = 0
    return h, m, "{:02d}:{:02d}".format(h, m)


#----- Ephemeris data

ephem_data = {}


def read_astro(text):
    '''Parses the ephemeris text'''

    global ephem_data

    for text_line in text.split('\n'):
        if not text_line or text_line[0] == '#':
            continue
        body_ephem = text_line.split(',')

        if COUNTRY == 'Fr':
            body_name = body_list_fr[body_ephem[0].strip()]
        else:
            body_name = body_ephem[0].strip()

        ephem_data[body_ephem[0]] = {
            'body': body_name,
            'date': body_ephem[1].strip(),
            'rise': body_ephem[2].strip(),
            'az_rise': body_ephem[3].strip(),
            'trans': body_ephem[4].strip(),
            'elev': body_ephem[5].strip(),
            'set': body_ephem[6].strip(),
            'az_set': body_ephem[7].strip()
        }
        print_debug("%s@%s: %s@%s, %s@%s, %s@%s" %
                (body_ephem[0], body_ephem[1], body_ephem[2], body_ephem[3], body_ephem[4], body_ephem[5], body_ephem[6], body_ephem[7]))
    return


def get_ephem_data():
    '''Fetches astro data from IMCCE'''

    print_entry("Reading astro data...")

    astro_text = fetch_data_text(display, EPHEM_URL %
                                 (current['date_ymd'], LONG, LAT))
    if astro_text:
        read_astro(astro_text)
        print_exit("...success reading astro data")
        return True
    else:
        print_error("...error reding astro data")
        return False
     

#----- ISS data

def get_iss_data():
    '''Gets the ISS position data'''

    global lat_iss, long_iss

    print_entry("Reading ISS data...")
    iss_json = fetch_data_json(display, ISS_URL)
    if not iss_json:
        print_error("...error reading ISS data")
        return False
    print_debug(iss_json)
    try:
        lat_iss = float(iss_json['iss_position']['latitude'])
        long_iss = float(iss_json['iss_position']['longitude'])
        print_debug("Position: Lat = %s, Long = %s" % (lat_iss, long_iss))
        print_exit("...success reading ISS data")
        return True
    except Exception as e:
        print_error("...error reading ISS data: %s" %(e))
        return False


#----- Moon data

def calculate_phase(p, d):
    '''Calculates moon phase from the phase in degrees'''

    ix = round(p / 45)
    if d > 0:
        return dirs_cr[ix], jpg_cr[ix]
    else:
        return dirs_dc[ix], jpg_dc[ix]


def read_moon(moon_json):
    '''Parses the moon data json'''

    global moon_phase, moon_dec, moon_ra, moon_rise_hm, moon_set_hm
    
    print_entry("Parsing moon data...")
    if not moon_json:
        return False
    print_debug(moon_json)
    
    try:
        moon_phase = float(moon_json["data"][0]["phase"])
        moon_dec = float(moon_json["data"][0]["dec"])
        moon_ra = float(moon_json["data"][0]["ra"])
        
        # Gets the moon rise local time
        try:
            moon_rise_h, moon_rise_m, moon_rise_hm = hm_local_convert(ephem_data['Moon']['rise'])
        except:
            moon_rise_hm = ''
            
        # Gets the moon set local time
        try:
            moon_set_h, moon_set_m, moon_set_hm = hm_local_convert(ephem_data['Moon']['set'])
        except:
            moon_set_hm = ''
            
        print_debug("Phase = %0.0f, dec = %0.0f, ra = %0.0f, rise = %s, set = %s" %
                  (moon_phase, moon_dec, moon_ra, moon_rise_hm, moon_set_hm))
        print_exit("...success parsing moon data")
        return True
    except:
        moon_phase = 0.
        moon_dec = 0.
        print_error("...error parsing moon data")
        return False


def get_moon_data():
    '''Gets the Moon phase data'''
    
    print_entry("Getting moon data...")
    moon_json = fetch_data_json(display, MOON_URL %
                                (current["date_ymd"], current["time_hm"]))
    if moon_json:
        read_moon(moon_json)
        print_exit("...success getting moon data")
        return True
    else:
        print_error("...error getting moon data")
        return False

#----- Alla astro data

def get_astro_data():
    '''Get the astro data'''

    global iss_ok, ephem_ok, moon_ok
    print_entry("Getting all astro data...")
    display.led(128)
    display_status(display, 'Fetching astro data')
    currenttime()
    iss_ok = get_iss_data()
    ephem_ok = get_ephem_data()
    moon_ok = get_moon_data()
    display.led(0)
    print_exit("...success getting all astro data")
    return


#-------------------------------------------------
#		Display functions
#-------------------------------------------------

#----- Ephem display

x_0h = 105
x_24h = 255

def display_visi(body, y):
    '''Displays the body visibility from coordinates y'''

    display.set_pen(0)
    display.set_font("bitmap8")

    flush_text_right(display, ephem_data[body]['body'], x_0h - 30, y, 2)

    display.line(x_0h, y + 10, x_24h, y + 10)
    rise_h, rise_m, rise_hm = hm_local_convert(ephem_data[body]['rise'])
    set_h, set_m, set_hm = hm_local_convert(ephem_data[body]['set'])
    display.text(rise_hm, x_0h - 25, y + 6, 20, 1)
    display.text(set_hm, x_24h + 5, y + 6, 20, 1)
    d = x_24h - x_0h
    r = int((rise_h + rise_m / 60) * d / 24)
    s = int((set_h + set_m / 60) * d / 24) 
    if r < s:
        display.rectangle(r + x_0h, y + 8, s - r, 8)
    else:
        display.rectangle(x_0h, y + 8, s, 8)
        display.rectangle(x_0h + r, y + 8, d - r, 8)
    return


def display_astro():
    '''Displays the current ephemeris information'''

    print_entry("Display astro data...")
    
    display.set_pen(0)
    display.set_font("bitmap8")

    y = 22

    for body in body_list:
        display_visi(body, y)
        y+= 15

    print_exit("...display astro completed")
    return


def draw_ephem_page():
    '''Displays the current ephemeris tab'''

    print_entry("Display ephem info ...")
    display_title(display, "%s %s, %s %s" %
                  (TAB_NAMES[0], LOCATION, current["wd"], current["date_dm"]))

    if ephem_ok:
        display_astro()

    print_exit("...display ephem info completed")
    return 


#----- ISS display

x_iss_map = 110
y_iss_map = 0

def mapLatLongToXY(lat, lon):
    '''Converts Lat & Lon into x & y position on the map'''

    x = (int)(0.49 * lon + 87.5) % 175 + x_iss_map
    y = (int)(-0.67 * lat + 60) + y_iss_map
    return x, y


def draw_iss_tab():
    '''Displays the current ISS position'''

    print_entry("ISS info display...")
    if iss_ok:
        display_title(display, TAB_NAMES[1], x_iss_map)
        display.set_pen(0)
        display.text("%s %s" % (current["wd"], current["date_dm"]), 4, 24)
        display.text(current["time_hm"], 4, 44)
        display.text("Lat", 4, 64)
        if lat_iss < 0:
            display.text("%0.0f S" % (-lat_iss), 60, 64)
        else:
            display.text("%0.0f N" % (lat_iss), 60, 64)
        display.text("Long", 4, 84)
        if long_iss < 0:
            display.text("%0.0f W" % (-long_iss), 60, 84)
        else:
            display.text("%0.0f E" % (long_iss), 60, 84)

        jpeg.open_file(ISS_MAP)
        jpeg.decode(x_iss_map, y_iss_map, jpegdec.JPEG_SCALE_FULL)

        x, y = mapLatLongToXY(lat_iss, long_iss)
        print_debug("Lat = %s, Long = %s, x = %s, y = %s" %
                    (lat_iss, long_iss, x, y))
        display.set_pen(0)
        display.line(x, y_iss_map, x, 120)
        display.line(x_iss_map, y, 175 + x_iss_map, y)

    print_exit("...ISS info display completed")
    return


#----- Moon display

x_moon_map = 180
y_moon_map = 14

def draw_moon_tab():
    '''Displays the moon phase'''

    print_entry("Moon info display...")
    if moon_ok:
        phase_name, phase_jpg = calculate_phase(moon_phase, moon_dec)
        moon_jpg = MOONDIR + phase_jpg + '.jpg'
        print_debug("Moon JPG = %s" % (moon_jpg))
        jpeg.open_file(moon_jpg)
        jpeg.decode(x_moon_map, y_moon_map, jpegdec.JPEG_SCALE_FULL)

        display_title(display, TAB_NAMES[2], x_moon_map)

        display.set_pen(0)
        display.text("%s %s %s" % (current["wd"], current["date_dm"], current["time_hm"]), 4, 24)
        display.text("Phase: %0.0f° (%s)" % (moon_phase, phase_name), 4, 44)
        # display.text("RA: %0.0f°" % (moon_ra), 4, 64)
        # display.text("Dec: %0.0f°" % (moon_dec), 4, 84)
        display.text(RISE_SET[0], 4, 64)
        display.text(RISE_SET[1], 4, 84)

        display.text(moon_rise_hm, display.measure_text(RISE_SET[0]) + 10, 64)
        display.text(moon_set_hm, display.measure_text(RISE_SET[1]) + 10, 84)

    print_exit("...Moon info display completed")
    return


#----- General display

def draw_astro_tab():
    '''Displays astro information tabs'''

    print_entry("Astro info display tab %s..." % (tab))

    display_clear(display)
    display_menu(display)

    if tab == 0:
        draw_ephem_page()
    elif tab == 1:
        draw_iss_tab()
    else:
        draw_moon_tab()

    display_tab_status(display, tab, TAB_NB)
    display.update()

    print_exit("...Astro info display completed")
    return


#-------------------------------------------------
#		Main
#-------------------------------------------------

def astro():
    '''Main loop to displays astro tabs according to the key pressed'''

    global tab

    changed = False
    renew = True


    while True:

        if renew:
            print_entry("Collecting astro data...")
            get_astro_data()
            renew = False
            changed = True
            print_exit("...astro data collected")

        if changed:
            print_entry("Displaying astro data...")
            draw_astro_tab()
            changed = False
            print_exit("...astro data displayed")
            print_entry("Waiting for key pressed...")

        # Call halt in a loop, on battery this switches off power.
        # On USB, the app will exit when A+C is pressed because the launcher picks that up.
        display.halt()

        if display.pressed(badger2040.BUTTON_DOWN):
            print_exit("...Button down detected")
            tab += 1
            tab = tab % TAB_NB
            changed = True

        if display.pressed(badger2040.BUTTON_UP):
            print_exit("...Button up detected")
            tab -= 1
            tab = tab % TAB_NB
            changed = True
        
        if display.pressed(badger2040.BUTTON_A):
            print_exit("...Button ASTRO detected")
            renew = True
            changed = True
        
        if display.pressed(badger2040.BUTTON_B):
            print_exit("...Button WEATHER detected")
            launch_pages("weather")

        if display.pressed(badger2040.BUTTON_C):
            print_exit("...Button DATA detected")
            launch_pages("data")
            
        # sleep(0.5)


# Start of the script 

print(">> START astro <<")

# Launch the loop
astro()

#-------------------------------------------------
#----- FIN DU PROGRAMME --------------------------
#-------------------------------------------------
