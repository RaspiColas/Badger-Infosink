#!/usr/bin/python
# -*- coding: utf-8 -*-

#---------------------------------------------------#
#													#
#				weather_badger.py					#
#													#
#---------------------------------------------------#

"""
Python script to grab weather data and displays them on Badger 2040 : 
- current weather condition
- forecast for the next 4 days 

Fetches info from openweathermap

Requires 
- Weather images in  /wicons/
- Wind direction images in /windir/
- common_badger.py library of common functions and data
- Fill up OPENWEATHER_ID

"""

import badger2040w as badger2040
import jpegdec
from time import localtime

from common_badger import *


# VERBOSE = False

FORECAST_NB = 4
TAB_NB = FORECAST_NB + 1
tab = 0  # Let's start with "Current weather" tab !

OPENWEATHER_ID = "OPENWEATHER_ID"
OPENWEATHER_FOR = "http://api.openweathermap.org/data/2.5/forecast?q=%s&units=metric&appid=%s"
OPENWEATHER_WEA = "http://api.openweathermap.org/data/2.5/weather?q=%s&units=metric&appid=%s"

WICONDIR = "/wicons/"
WINDCONDIR = "/windir/"

icon_mapping = {
    "01d": "icon-sun.jpg",
    "01n": "icon-sun.jpg",
    "02d": "icon-few-cloud.jpg",
    "02n": "icon-few-cloud.jpg",
    "03d": "icon-clouds.jpg",
    "03n": "icon-clouds.jpg",
    "04d": "icon-clouds.jpg",
    "04n": "icon-clouds.jpg",
    "09d": "icon-rain.jpg",
    "09n": "icon-rain.jpg",
    "10d": "icon-rain.jpg",
    "10n": "icon-rain.jpg",
    "11d": "icon-storm.jpg",
    "11n": "icon-storm.jpg",
    "13d": "icon-snow.jpg",
    "13n": "icon-snow.jpg",
    "50d": "icon-myst.jpg",
    "50n": "icon-myst.jpg"
}

icon_sm_mapping = {
    "01d": "icon-sm-sun.jpg",
    "01n": "icon-sm-sun.jpg",
    "02d": "icon-sm-few-cloud.jpg",
    "02n": "icon-sm-few-cloud.jpg",
    "03d": "icon-sm-clouds.jpg",
    "03n": "icon-sm-clouds.jpg",
    "04d": "icon-sm-clouds.jpg",
    "04n": "icon-sm-clouds.jpg",
    "09d": "icon-sm-rain.jpg",
    "09n": "icon-sm-rain.jpg",
    "10d": "icon-sm-rain.jpg",
    "10n": "icon-sm-rain.jpg",
    "11d": "icon-sm-storm.jpg",
    "11n": "icon-sm-storm.jpg",
    "13d": "icon-sm-snow.jpg",
    "13n": "icon-sm-snow.jpg",
    "50d": "icon-sm-myst.jpg",
    "50n": "icon-sm-myst.jpg"
}

if COUNTRY == "Fr":
    WEATHER_CODE_MAPPING = {
        "01d": "Soleil",
        "01n": "Nuit claire",
        "02d": "Partiellement nuageux",
        "02n": "Partiellement nuageux",
        "03d": "Nuages épars",
        "03n": "Nuages épars",
        "04d": "Quelques nuages",
        "04n": "Quelques nuages",
        "09d": "Averses",
        "09n": "Averses",
        "10d": "Pluie",
        "10n": "Pluie",
        "11d": "Orage",
        "11n": "Orage",
        "13d": "Neige",
        "13n": "Neige",
        "50d": "Brouillard ",
        "50n": "Brouillard "
    }
    TAB_NAMES = ["Météo", "Prévisions"]
else:
    WEATHER_CODE_MAPPING = {
        "01d":	"clear sky",
        "01n":	"clear sky",
        "02d":	"few clouds",
        "02n":	"few clouds",
        "03d":	"scattered clouds",
        "03n":	"scattered clouds",
        "04d":	"broken clouds",
        "04n":	"broken clouds",
        "09d":	"shower rain",
        "09n":	"shower rain",
        "10d":	"rain",
        "10n":	"rain",
        "11d":	"thunderstorm",
        "11n":	"thunderstorm",
        "13d":	"snow",
        "13n":	"snow",
        "50d":	"mist ",
        "50n":	"mist "
    }
    TAB_NAMES = ["Weather", "Forecast"]


dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']


# Display Setup

display = badger2040.Badger2040W()
jpeg = jpegdec.JPEG(display.display)
display.set_update_speed(2)


#-------------------------------------------------
#		Weather functions
#-------------------------------------------------

forecast_data = {}
weather_data = {
    'weekday': '',
    'nameday': '?',
    'utc': 0,
    'time': '?',
    'temp': '?',
    'condition_code': '?',
    'condition_name': '?'
}


def calculate_bearing(d):
    '''Calculates a compass direction from the wind direction in degrees'''

    ix = round(d / (360. / len(dirs)))
    return dirs[ix % len(dirs)]


def get_weather_data():
    '''Fetches weather data from Open Weather Map'''

    global weather_data

    print_entry("Reading weather data...")

    weather_json = fetch_data_json(display, OPENWEATHER_WEA % (LOCATION + ',' + COUNTRY, OPENWEATHER_ID))
        
    if not weather_json:
        print_error("...error: cannot read weather")
        return False
    
    print_debug(weather_json)
    print_exit("...success reading weather data")

    # parse relevant data from JSON

    print_entry("Parsing weather data...")
    utc = 0
    print_debug('weather_json["dt"]= %s' % (weather_json["dt"]))

    try:
        try:

            utc = int(weather_json["dt"])

            dt = localtime(utc)
            
            wd = int(dt[6])
            hr = '{:02d}:{:02d}'.format(dt[3] + TIMEZONE, dt[4])
            
            wd_name = WEEKDAYS[wd]

        except:
            utc = 0
            wd = ''
            hr = '00:00'
            wd_name = ''

        print_debug("UTC = %s, WD = %s, hr = %s" %(utc, wd_name, hr))

        try:
            temp = float(weather_json["main"]["temp"])
        except:
            temp = 0.
        try:
            wind = float(weather_json["wind"]["speed"]) * 3.6
        except:
            wind = 0.
        try:
            wind_dir = calculate_bearing(weather_json["wind"]["deg"])
        except:
            wind_dir = '?'
        try:
            code_current = weather_json["weather"][0]["icon"]
            weather_name = WEATHER_CODE_MAPPING[code_current]
        except:
            code_current = '?'
            weather_name = '?'

        print_debug("%s@%s, %0.0f°C, %0.0fkm/h, %s, %s" %
                  (wd_name, hr, temp, wind, wind_dir, weather_name))
        weather_data['utc'] = utc
        weather_data['time'] = hr
        weather_data['weekday'] = wd
        weather_data['nameday'] = wd_name

        weather_data['temp'] = temp
        weather_data['wind'] = wind
        weather_data['wind_dir'] = wind_dir
        weather_data['condition_code'] = code_current
        weather_data['condition_name'] = weather_name
        print_exit("...success parsing weather info")
        return True

    except Exception as e:
        print_error("...error parsing weather info: %s" % (e))
        return False


def get_forecast():
    '''Fetches forecast data from Open Weather Map'''

    global forecast_data

    print_entry("Reading forecast data...")
    weather_forecast = fetch_data_json(display, OPENWEATHER_FOR % (LOCATION + ',' + COUNTRY, OPENWEATHER_ID))

    if not weather_forecast:
        print_error("...error: cannot read forecast data")
        return False
    print_exit("...success reading forecast data")

    #----- Extracts weather forecast data
    try:
        forecast_list = weather_forecast["list"]

        print_debug(forecast_list)

        day_num = -1
        wd = -1
        wd_name = ''

        for forecast in forecast_list:
            try:
                utc = int(forecast["dt"])
                dt = localtime(utc)
                wd_new = int(dt[6])
                hr = '{:02d}'.format(dt[3])
                time = '{:02d}:{:02d}'.format(dt[3], dt[4])
            except:
                utc = 0
                wd_new = 0
                hr = '00:00'
            try:
                temp = float(forecast["main"]["temp"])
            except:
                temp = 0.
            try:
                wind = float(forecast["wind"]["speed"]) * 3.6
            except:
                wind = 0.
            try:
                wind_dir = calculate_bearing(forecast["wind"]["deg"])
            except:
                wind_dir = '?'
            try:
                code = forecast["weather"][0]["icon"]
                print_debug("Weather code %s" % (code))
                weather_name = WEATHER_CODE_MAPPING[code]
            except:
                print_debug("Weather name unknown")
                code = '?'
                weather_name = '?'

            if wd != wd_new:
                wd = wd_new
                
                day_num += 1
                try:
                    wd_name = WEEKDAYS[wd]
                except:
                    wd_name = ''

                forecast_data[day_num] = {
                    'weekday': wd,
                    'nameday': wd_name,
                    'hours': {}
                }
            print_debug("Forecast for day %s@%s: %s°C, %skm/h %s, %s" %
                        (day_num, time, temp, wind, wind_dir, weather_name))
                                
            forecast_data[day_num]['hours'][hr] = {
                'time': time,
                'temp': temp,
                'wind': wind,
                'wind_dir': wind_dir,
                'condition_code': code,
                'condition_name': weather_name
            }

            print_debug("%s@%s, %0.0f°C, %0.0fkm/h, %s, %s" %
                    (wd_name, hr, temp, wind, wind_dir, weather_name))

        return True
    
    except Exception as e:
        print_error("...error reading forecast data: %s" % (e))
        return False


def get_weather_forecast():
    """
        Fetches forecast and weather data
    """

    global weather_ok, forecast_ok

    display.led(128)
    display_status(display, 'Fetching weather data')
    weather_ok = get_weather_data()
    forecast_ok= get_forecast()
    display.led(0)
    return


#-------------------------------------------------
#		Display functions
#-------------------------------------------------

def display_current_weather():
    '''Displays current weather information'''

    print_entry("Display current weather...")

    try:
        # Draw the tab header
        display_title(display, "%s %s, %s %s" % (
            TAB_NAMES[0], LOCATION, weather_data['nameday'], weather_data['time']))

        display.set_font("bitmap8")
        jpeg_file = WICONDIR + icon_mapping[weather_data['condition_code']]
        print_debug("Opening %s" % (jpeg_file))
        jpeg.open_file(jpeg_file)
        jpeg.decode(13, 30, jpegdec.JPEG_SCALE_FULL)
        jpeg.open_file(WICONDIR + "icon-tn-wind.jpg")
        jpeg.decode(98, 68, jpegdec.JPEG_SCALE_FULL)
        display.set_pen(0)
        display.text(weather_data['condition_name'],
                     int(296 / 3), 28, 296 - 105, 2)
        display.text("T°", int(296 / 3), 48, 296 - 105, 2)
        display.text("%0.0f °C" % (weather_data['temp']),
                     int(296 / 3) + 60, 48, 296 - 105, 2)
        # display.text("Vent:", int(296 / 3), 68, 296 - 105, 2)
        display.text("%0.0f km/h" % (weather_data['wind']),
                     int(296 / 3) + 60, 68, 296 - 105, 2)

        display.text(weather_data['wind_dir'], 188, 88, 296 - 105, 2)
        jpeg.open_file(WINDCONDIR + weather_data['wind_dir'] + '.jpg')
        jpeg.decode(158, 88, jpegdec.JPEG_SCALE_FULL)
        print_exit("...display weather completed")
    except Exception as e:
        display.set_pen(0)
        display.rectangle(0, 60, 296, 25)
        display.set_pen(15)
        display.text("Unable to display weather!", 5, 65, 296, 1)
        print_exit("...unable to display weather: %s" %(e))
    return


def display_forecast(day):
    '''Displays forecast information'''

    print_entry("Displaying forecast for day %s..." %(day))

    forecast_displayed = False
    try:
        daily_forecast = forecast_data[day]
        # Draw the tab header
        display_title(display, "%s %s, %s" %
                      (TAB_NAMES[1], LOCATION, forecast_data[day]['nameday']))
        # display.update()

        display.set_font("bitmap8")
        s = 2
        # display.set_font("sans")

        display.line(26, 20, 26, 120)
        display.line(116, 20, 116, 120)
        display.line(206, 20, 206, 120)
        jpeg.open_file(WICONDIR + "icon-tn-wind.jpg")
        jpeg.decode(0, 88, jpegdec.JPEG_SCALE_FULL)
        display.set_pen(0)
        display.text("T°", 3, 60, 40, s)


        for hr in daily_forecast['hours']:
            print_debug("Checking forecast for %s@%s" % (day, hr))

            daily_forecast_hr = daily_forecast['hours'][hr]

            if hr == '09':
                x_hr = 26
                forecast_displayed = True
            elif hr == '12':
                x_hr = 116
                forecast_displayed = True
            elif hr == '18':
                x_hr = 206
                forecast_displayed = True
            else:
                continue

            print_debug("Displaying forecast for %s : %s" %
                        (hr, daily_forecast_hr['condition_code']))
                
            jpeg.open_file(WICONDIR + icon_sm_mapping[daily_forecast_hr['condition_code']])
            jpeg.decode(x_hr + 25, 20, jpegdec.JPEG_SCALE_FULL)

            display.set_pen(0)

            center_text(display, "%0.0f °C" %
                        (daily_forecast_hr['temp']), x_hr+45, 60, s)
            center_text(display, "%0.0f km/h" %
                        (daily_forecast_hr['wind']), x_hr+45, 80, s)

            display.text("%s" % (daily_forecast_hr['wind_dir']), x_hr+45, 100, x_hr + 100, s)
            jpeg.open_file(WINDCONDIR + daily_forecast_hr['wind_dir'] + '.jpg')
            jpeg.decode(x_hr + 20, 98, jpegdec.JPEG_SCALE_FULL)

        if forecast_displayed:
            print_exit("...display forecast completed")
        else:
            print_exit("...no forecast to be displayed")

    except Exception as e:
        display.set_pen(0)
        display.rectangle(0, 60, 296, 25)
        display.set_pen(15)
        display.text("Unable to display weather!", 5, 65, 296, 1)
        print_exit("...unable to display weather: %s" %(e))
    return forecast_displayed


def display_weather(tab):
    '''Displays either the current weather (tab = 0) or the forecast (tab > 0) information'''

    if tab == 0:
        display_current_weather()
        weather_displayed = True
    else:
        weather_displayed = display_forecast(tab-1)
    return weather_displayed


def display_weather_tab():
    '''Displays the current tab (unless forecast is empoty because we are the end of the day)'''

    global tab

    weather_displayed = False

    display_clear(display)
    display_menu(display)

    while not weather_displayed:

        print_entry("Weather info display tab %s..." %(tab))

        weather_displayed = display_weather(tab)
        if not weather_displayed:
            print_exit("...cannot display weather for tab %s" % (tab))
            tab = (tab + 1) % (TAB_NB)
        else:
            print_exit("...weather info displayed for tab %s" % (tab))

    display_tab_status(display, tab, TAB_NB)
    display.update()

    return 


#-------------------------------------------------
#		Main
#-------------------------------------------------

def weather():
    '''Main loop to displays weather tabs according to the key pressed'''

    global tab

    tab = 0
    
    changed = False
    renew = True

    while True:

        if renew:
            print_entry("Collecting weather data...")
            get_weather_forecast()
            renew = False
            changed = True
            print_exit("...weather data collected")

        if changed:
            print_entry("Generating weather page...")
            display_weather_tab()
            changed = False
            print_exit("...weather data displayed")
            print_entry("Waiting for key pressed...")

        # Call halt in a loop, on battery this switches off power.
        # On USB, the app will exit when A+C is pressed because the launcher picks that up.
        display.halt()

        if display.pressed(badger2040.BUTTON_DOWN):
            print_exit("...button down detected")
            tab += 1
            tab = tab % (TAB_NB)
            changed = True

        if display.pressed(badger2040.BUTTON_UP):
            print_exit("...button up detected")
            tab -= 1
            tab = tab % (TAB_NB)
            changed = True
        
        if display.pressed(badger2040.BUTTON_A):
            print_exit("...button ASTRO detected")
            launch_pages("astro")
        
        if display.pressed(badger2040.BUTTON_B):
            print_exit("...button WEATHER detected")
            renew = True
            changed = True

        if display.pressed(badger2040.BUTTON_C):
            print_exit("...button DATA detected")
            launch_pages("data")


# Start of the script
print(">> START weather <<")

# Launch the loop
weather()

#-------------------------------------------------
#----- FIN DU PROGRAMME --------------------------
#-------------------------------------------------
