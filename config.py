from datetime import timedelta as _timedelta
from pytz import timezone as _timezone

# IP address
# Set '0.0.0.0' to open for all IPv4 addresses on this local machine
IP = '0.0.0.0'

# PORT of this application
PORT = 80

# Debug
DEBUG = True

# Set time zone of website
TIME_ZONE = _timezone('Asia/Hong_Kong')

# Time section that is only available for booking after a period of time
BOOK_TIME = _timedelta(days=7)

# Sever Mode (0: development server) (1: production WSGI server)
SERVER_MODE = 0

# Time that session will be expired after last action 
SESSION_LIFETIME = _timedelta(days=0, hours=0, minutes=30)