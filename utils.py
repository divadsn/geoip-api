import json
import dicttoxml
import config
import socket
from os import path

from flask import Response
from dicttoxml import dicttoxml as output_xml
from geoip2.database import Reader
from geoip2.errors import AddressNotFoundError

# Turn off log output for dicttoxml
dicttoxml.set_debug(config.DEBUG)

JSON_MAPPING = {
    "ip_address": "",
    "hostname": "",
    "city": {},
    "country": {},
    "location": {},
    "asn": {}
}

# Fetch GeoIP data from GeoLite2 database
def fetch_geoip(ip_address, language=None):
    # Copy response json mapping
    response = dict(JSON_MAPPING)

    # Get hostname from IP address, pass if fail
    try:
        response['ip_address'] = ip_address
        response['hostname'] = socket.gethostbyaddr(ip_address)[0]
    except Exception as ex:
        pass

    # Load GeoLite2 City database
    geocity = Reader(path.join(config.MMDB_PATH, "GeoLite2-City.mmdb"))

    # Try to fetch data and build response, otherwise raise exception
    try:
        data = geocity.city(ip_address)

        # geoip.city
        response['city']['name'] = data.city.name
        response['city']['id'] = data.city.geoname_id
        response['city']['region'] = data.subdivisions.most_specific.name
        response['city']['region_code'] = data.subdivisions.most_specific.iso_code

        # geoip.location
        response['location']['accuracy_radius'] = data.location.accuracy_radius
        response['location']['zip'] = data.postal.code
        response['location']['latitude'] = data.location.latitude
        response['location']['longitude'] = data.location.longitude
        response['location']['timezone'] = data.location.time_zone

        # geoip.country
        response['country']['name'] = data.country.name
        response['country']['iso_code'] = data.country.iso_code
        response['country']['continent'] = data.continent.name
        response['country']['continent_code'] = data.continent.code
        response['country']['is_eu'] = data.country.is_in_european_union
    except AddressNotFoundError as ex:
        raise ex


    # Load GeoLite2 ASN database (optional)
    geoasn = Reader(path.join(config.MMDB_PATH, "GeoLite2-ASN.mmdb"))

    # Try to fetch data and build response, otherwise skip
    try:
        data = geoasn.asn(ip_address)

        # geoip.asn
        response['asn']['name'] = data.autonomous_system_organization
        response['asn']['id'] = data.autonomous_system_number
    except AddressNotFoundError as ex:
        pass

    # Close database instances
    geocity.close()
    geoasn.close()

    # Strip off empty sections
    for k in [k for k,v in response.items() if not v or None]:
        del response[k]

    # Return built response object
    return response

# Prepare custom Flask response with additional options like CORS enabled
def prepare_response(data, status, output_format="json", callback=None, root="geoip"):
    if output_format == "json":
        response = json.dumps(data, skipkeys=True)
        if callback is not None:
            response = "%s(%s)" % (callback, response)
    elif output_format == "xml":
        response = output_xml(data, custom_root=root, attr_type=False)
    else:
        return error("Unknown output format %s" % output_format, 500)

    return Response(
        response=response,
        status=status,
        headers={
            "Access-Control-Allow-Origin": "*"
        },
        mimetype="application/" + output_format)

# Return response with error code and custom XML root
def error(message, status, output_format="json", callback=None):
    return prepare_response({"message": message}, status, output_format, callback, "error")