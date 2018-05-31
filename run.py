from waitress import serve
from server import app

if __name__ == "__main__":
    serve(app, host=app.config['LISTEN_ADDR'], port=app.config['PORT'])