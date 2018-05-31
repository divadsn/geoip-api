import config
import logging
import json
from os import path

from flask import Flask, Response, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from validators import ipv4, ipv6
from geoip2.database import Reader

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

@app.route("/<ip_address>", methods=["GET"])
@limiter.limit(config.RATE_LIMIT)
def geoip(ip_address):
    # Check if ip_address is a valid IPv4 or IPv6 address
    if not ipv4(ip_address) and not ipv6(ip_address):
        return jsonify({
            "message": ip_address + " does not appear to be an IPv4 or IPv6 address" 
        }), 400

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

@app.route("/", methods=["GET"])
@limiter.limit(config.RATE_LIMIT)
def mygeoip():
    # Check if an IP address got specified as parameter or return visitors IP
    return geoip(request.args.get("ip") or request.remote_addr)
    
@app.errorhandler(404)
def not_found(e):
    # Give a unfunny 404 not found message back
    return jsonify({"message": "What are you even looking here for?"}), 404