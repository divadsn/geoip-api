import json
import dicttoxml
import config # TODO: Read config values from app.config
import socket
from os import path

from flask import Response
from dicttoxml import dicttoxml as output_xml
from geoip2.database import Reader
from geoip2.errors import AddressNotFoundError

# Turn off log output for dicttoxml
dicttoxml.set_debug(config.DEBUG)

# Fetch GeoIP data from GeoLite2 database
def fetch_geoip(ip_address, language=None):
    # Prepare response object
    response = {}

    # Get hostname from IP address, pass if fail
    try:
        response['ip_address'] = ip_address
        response['hostname'] = socket.gethostbyaddr(ip_address)[0]
    except Exception as ex:
        pass

    # Load GeoLite2 City database
    geoip = Reader(path.join(config.MMDB_PATH, "GeoLite2-City.mmdb"))

    # Try to fetch data and build response, otherwise raise exception
    try:
        data = geoip.city(ip_address)

        # geoip.city
        response['city'] = {
            "name": data.city.name,
            "id": data.city.geoname_id,
            "region": data.subdivisions.most_specific.name,
            "region_code": data.subdivisions.most_specific.iso_code
        }

        # geoip.country
        response['country'] = {
            "name": data.country.name,
            "iso_code": data.country.iso_code,
            "continent": data.continent.name,
            "continent_code": data.continent.code,
            "is_eu": data.country.is_in_european_union
        }

        # geoip.location
        response['location'] = {
            "accuracy_radius": data.location.accuracy_radius,
            "zip": data.postal.code,
            "latitude": data.location.latitude,
            "longitude": data.location.longitude,
            "timezone": data.location.time_zone
        }
    except AddressNotFoundError as ex:
        raise ex

    # Close database instances
    geoip.close()

    # Load GeoLite2 ASN database (optional)
    response['asn'] = fetch_asn(ip_address)

    # Return built response object
    return response

# Fetch GeoIP ASN data from GeoLite2 database
def fetch_asn(ip_address):
    # Check if INCLUDE_ASN is True before proceeding
    if not config.INCLUDE_ASN:
        return None

    # Load GeoLite2 ASN database
    geoasn = Reader(path.join(config.MMDB_PATH, "GeoLite2-ASN.mmdb"))

    # Try to fetch data and build response, otherwise return empty
    try:
        data = geoasn.asn(ip_address)
        return {
            "name": data.autonomous_system_organization,
            "id": data.autonomous_system_number
        }
    except AddressNotFoundError:
        return {}
    finally:
        geoasn.close()
    

# Prepare custom Flask response with additional options like CORS enabled
def prepare_response(data, status, output_format="json", callback=None, root="geoip"):
    if output_format == "json":
        response = json.dumps(data, skipkeys=True)
    elif output_format == "xml":
        response = output_xml(data, custom_root=root, attr_type=False)
    else:
        return error("Unknown output format %s" % output_format, 500)

    # Apply custom decorator for JSONP and change output_format
    if callback is not None and output_format == "json":
        response = "%s(%s)" % (callback, response)
        output_format = "javascript"

    return Response(
        response=response,
        status=status,
        headers={
            "Access-Control-Allow-Origin": "*",
            "X-Powered-By": "python:divadsn/geoip-api"
        },
        mimetype="application/" + output_format)

# Return response with error code and custom XML root
def error(message, status, output_format="json", callback=None):
    return prepare_response({"message": message}, status, output_format, callback, "error")