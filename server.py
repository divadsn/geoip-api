import config

from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from validators import ipv4, ipv6
from waitress import serve

from utils import fetch_geoip, prepare_response, error

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config)

# Initialize limiter
limiter = Limiter(app, key_func=get_remote_address, default_limits=[app.config['RATE_LIMIT']])

# API Docs and about page
@app.route("/")
def index():
    return "Hello World!"

# Return geolocation data for provided IP address, with different language optional
@app.route("/<ip_address>", defaults={"language": app.config['LANGUAGE']})
@app.route("/<ip_address>/<language>")
def geoip(ip_address, language):
    # Get additional parameters from request
    output_format = request.args.get("output_format") or app.config['OUTPUT_FORMAT']
    callback = request.args.get("callback")

    # Check if ip_address is a valid IPv4 or IPv6 address
    if not ipv4(ip_address) and not ipv6(ip_address):
        return error(ip_address + " does not appear to be an IPv4 or IPv6 address", 400, output_format, callback)

    # Try to fetch data from GeoLite2 databases
    try:
        data = fetch_geoip(ip_address) # TODO: Add multi-language support
    except Exception as ex:
        return error(str(ex), 404, output_format, callback)

    return prepare_response(data, 200, output_format, callback)

# Give a unfunny 404 not found message back
@app.errorhandler(404)
def not_found(e):
    return error("What are you even looking here for?", 404)

# Return an error if ratelimit has been exceeded
@app.errorhandler(429)
def ratelimit_handler(e):
    return error("Ratelimit exceeded %s" % e.description, 429)

# Run the app!
if __name__ == "__main__":
    serve(app, host=app.config['LISTEN_ADDR'], port=app.config['PORT'])