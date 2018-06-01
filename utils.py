import json

from flask import Response


def prepare_response(data, status, output_format="json", callback=None):
    return Response(
        response=json.dumps(data),
        status=status,
        headers={
            "Access-Control-Allow-Origin": "*"
        },
        mimetype="application/" + output_format)

def error(message, status, output_format="json", callback=None):
    return prepare_response({"message": message}, status, output_format, callback)