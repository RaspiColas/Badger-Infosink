# Common badger functions

import badger2040w as badger2040
import urequests
import jpegdec
from time import localtime
import badger_os
import gc

VERBOSE = False

# Set your latitude/longitude here (find yours by right clicking in Google Maps!)
LAT = 48.828
LONG = -2.330
TIMEZONE = 2
LOCATION = "Paris"
COUNTRY = "Fr"

TRY_NB = 2

indent = 0

pages = {
    "astro": "astro_badger",
    "weather": "weather_badger",
    "data": "data_badger"
}

if COUNTRY == 'Fr':
    WEEKDAYS = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    RISE_SET = ["Lever:", "Coucher:"]
    PAGE_NAMES = ["Astro", "Météo", "Données"]
    MONTH_NAMES = ["Janv", "Fev", "Mar", "Avr", "Mai", "Juin", "Juil", "Aout", "Sept", "Oct", "Nov", "Dec"]
else:
    WEEKDAYS = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    RISE_SET = ["Rise:", "Set:"]
    PAGE_NAMES = ["Astro", "Weather", "Data"]
    MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sept", "Oct", "Nov", "Dec"]


#-------------------------------------------------
#		Connection management functions
#-------------------------------------------------

def fetch_data_text(display, url):
    """
        Fetches data as text
    """
    print_entry("Fetching text data from web...")
    for i in range(TRY_NB):
        try:
            r = urequests.get(url)
            txt = r.text
            r.close()
            print_exit("...fetching OK")
            return txt
        except Exception as e:
            print_debug("Attempt %s to connect" % (i))
            display.connect()
    print_error("...error fetching data")
    return ''


def fetch_data_json(display, url):
    '''Fetches data as json'''
    print_entry("Fetching json data from web...")
    for i in range(TRY_NB):
        try:
            r = urequests.get(url)
            j = r.json()
            r.close()
            print_exit("...fetching OK")
            return j
        except Exception as e:
            print_debug("Attempt %s to connect" % (i))
            display.connect()
    print_error("...error fetching data")
    return {}


#-------------------------------------------------
#		Memory management functions
#-------------------------------------------------

def launch_pages(pages_name):
    file = pages[pages_name]
    for k in locals().keys():
        if VERBOSE:
            print("process = " + k)
        if k not in ("gc", "file", "badger_os", "VERBOSE"):
            del locals()[k]
    gc.collect()
    badger_os.launch(file)
    return


#-------------------------------------------------
#		Printing functions
#-------------------------------------------------

warning = '\033[91m'
normal = '\033[0m'

def print_entry(text):
    global indent
    print("|  " * indent + text)
    indent += 1
    return

def print_exit(text):
    global indent
    indent -= 1
    print("|  " * indent + text)
    return

def print_error(text):
    global indent
    indent -= 1
    print("|  " * indent + warning + text + normal)
    return

def print_debug(text):
    if VERBOSE:
        print(text)
    return


#-------------------------------------------------
#		Text functions
#-------------------------------------------------

def flush_text_right(display, text, x, y, s):
    w = display.measure_text(text, s)
    display.text(text, max(x - w, 0), y, x, s)
    return


def center_text(display, text, x, y, s):
    w = display.measure_text(text, s)
    display.text(text, max(x - int(w/2), 0), y, w, s)
    return


def underline_text(display, text, x, y, s):
    w = display.measure_text(text, s)
    display.text(text, x, y, w, s)
    display.line(x, y+9, x+w, y+9)
    return


#-------------------------------------------------
#		Display functions
#-------------------------------------------------

def display_status(display, text):
    display.set_font("bitmap6")
    display.set_pen(0)
    display.rectangle(0, 0, 296, 140)
    display.set_pen(15)
    title_string = ">>> %s <<<" % (text)
    display.text(title_string, 148 -
                 int(display.measure_text(title_string)/2), 52)
    display.set_pen(0)
    display.update()
    return


def display_tab_status(display, t, tab_nb):
    y = 64 - tab_nb * 5
    for i in range(tab_nb):
        display.set_pen(0)
        display.rectangle(286, y, 8, 8)
        if i != t:
            display.set_pen(15)
            display.rectangle(287, y + 1, 6, 6)
        y += 10
    return


def display_title(display, title_string, h=296):
    '''Displays as a title the text in white over a black box h wide'''

    display.set_font("bitmap6")
    display.set_pen(0)
    display.rectangle(0, 0, h, 20)
    display.set_pen(15)
    w = display.measure_text(title_string)
    display.text(title_string, int((h - w) / 2), 4)
    display.set_pen(0)

    return


def display_menu(display):
    '''Displays bottom menu'''

    display.set_font("bitmap6")
    display.set_pen(0)
    display.rectangle(0, 118, 296, 10)
    display.set_pen(15)
    display.text(PAGE_NAMES[0], 40, 120, 100, 1)
    display.text(PAGE_NAMES[1], 136, 120, 100, 1)
    display.text(PAGE_NAMES[2], 242, 120, 100, 1)
    display.set_pen(0)
    return


def display_clear(display):
    display.set_pen(15)
    display.clear()
    display.set_pen(0)
    return


#-------------------------------------------------
#----- FIN DU PROGRAMME --------------------------
#-------------------------------------------------
