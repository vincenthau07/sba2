from app import create_app
import config
import os

os.environ['TZ'] = config.TIME_ZONE

#start website
app = create_app()

if __name__ == '__main__':
    app.debug=config.DEBUG
    app.run(host=config.IP, port=config.PORT)