from app import create_app
import config

#start website
app = create_app()

if __name__ == '__main__':
    if config.SERVER_MODE:
        from waitress import serve
        serve(app, host=config.IP, port=config.PORT)
    else:
        app.debug=config.DEBUG
        app.run(host=config.IP, port=config.PORT)