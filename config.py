from datetime import timedelta as _timedelta
from pytz import timezone as _timezone

# IP address
# Set '0.0.0.0' to open for all IPv4 addresses on this local machine
IP = '0.0.0.0'

# PORT of this application
PORT = 80

# Sever Mode (0: development server) (1: production WSGI server)
SERVER_MODE = 0

# Multithreading (for development server only)
THREADED = True

# Flask Debug Mode (for development server only)
DEBUG = True

# Set time zone of website
TIME_ZONE = _timezone('asia/Hong_Kong')

# Time section that is only available for booking after a period of time
BOOK_TIME = _timedelta(days=7)

# Time that session will be expired after last action 
SESSION_LIFETIME = _timedelta(days=0, hours=0, minutes=30)

# Google Oauth2 configs
CLIENT_ID = "486522423247-paab3n7imi4182bnioupbgn2tvkk1tba.apps.googleusercontent.com"
CLIENT_SECRET = "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"
