import json
import dicttoxml
import config

from flask import Response
from dicttoxml import dicttoxml as output_xml

# Turn off log output for dicttoxml
dicttoxml.set_debug(config.DEBUG)

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