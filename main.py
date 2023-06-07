#import launcher  # noqa F401
import badger2040w as badger2040
from common_badger import display_status

display = badger2040.Badger2040W()
display.led(128)

display_status(display, 'Connecting')
display.connect()

import astro_badger
