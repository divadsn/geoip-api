import config
import logging

from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from validators import ipv4, ipv6
from waitress import serve

from utils import fetch_geoip, prepare_response, error

# Initalize logger
logger = logging.getLogger("geoip")
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config)

# Initialize limiter
limiter = Limiter(app, key_func=get_remote_address)

# API Docs and about page
@app.route("/")
def index():
    return "Hello World!"

# Return geolocation data for provided IP address, with different language optional
@app.route("/<ip_address>", defaults={"language": app.config['LANGUAGE']})
@app.route("/<ip_address>/<language>")
@limiter.limit(app.config['RATE_LIMIT'])
def geoip(ip_address, language):
    # Check if output format is json or xml
    output_format = request.args.get("output_format") or app.config['OUTPUT_FORMAT']
    if output_format not in ("json", "xml"):
        return error("Wrong output format selected!", 400)

    # Check if output format has been requested and validate callback
    callback = request.args.get("callback")
    if callback is not None and output_format != "json":
        return error("You cannot request a jsonp callback when the output format is xml!", 400)

    # Check if ip_address is a valid IPv4 or IPv6 address
    if not ipv4(ip_address) and not ipv6(ip_address):
        return error(ip_address + " does not appear to be an IPv4 or IPv6 address", 400, output_format, callback)

    # Try to fetch data from GeoLite2 databases
    try:
        data = fetch_geoip(ip_address, language)
    except Exception as ex:
        return error(str(ex), 500, output_format, callback)

    return prepare_response(data, 200, output_format, callback)

# Give a unfunny 404 not found message back
@app.errorhandler(404)
def not_found(e):
    return error("What are you even looking here for?", 404)

# Run the app!
if __name__ == "__main__":
    serve(app, host=app.config['LISTEN_ADDR'], port=app.config['PORT'])