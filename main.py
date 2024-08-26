from app import create_app
import config
import os, datetime, time

tz = list(config.TIME_ZONE)
tz[3] = '-' if tz[3] == '+' else '+'
tz = ''.join(tz)
os.environ['TZ'] = tz


#start website
app = create_app()

if __name__ == '__main__':
    if config.SERVER_MODE:
        from waitress import serve
        serve(app, host=config.IP, port=config.PORT)
    else:
        app.debug=config.DEBUG
        app.run(host=config.IP, port=config.PORT)