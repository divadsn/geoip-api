import config
import logging
import json
from os import path

from flask import Flask, Response, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from validators import ipv4, ipv6
from geoip2.database import Reader

from utils import prepare_response, error

# Initalize logger
logger = logging.getLogger("geoip")
logging.basicConfig(level=logging.DEBUG)

# Load GeoLite2 databases
geocity = Reader(path.join(config.MMDB_PATH, "GeoLite2-City.mmdb"))
geocountry = Reader(path.join(config.MMDB_PATH, "GeoLite2-Country.mmdb"))
geoasn = Reader(path.join(config.MMDB_PATH, "GeoLite2-ASN.mmdb"))

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
@app.route("/<ip_address>", defaults={"language": config.LANGUAGE})
@app.route("/<ip_address>/<language>")
@limiter.limit(config.RATE_LIMIT)
def geoip(ip_address, language):
    # Check if output format is json or xml
    output_format = request.args.get("output_format") or config.OUTPUT_FORMAT
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
        city = geocity.city(ip_address)
        country = geocountry.country(ip_address)
        asn = geoasn.asn(ip_address)
    except Exception as ex:
        return jsonify({"message": str(ex)}), 500

    # Build response object
    response = {
        "ip_address": ip_address,
        "city": {
            "":""
        },
        "county": {
            "":""
        },
        "location": {
            "":""
        },
        "asn": {
            "":""
        }
    }

    return jsonify(response)

# Give a unfunny 404 not found message back
@app.errorhandler(404)
def not_found(e):
    return error("What are you even looking here for?", 404)