# Flask settings
LISTEN_ADDR = "localhost"
PORT = 8069
DEBUG = True # disable this for production

# API settings
MMDB_PATH = "/usr/share/GeoIP" # change this if using own copy
RATE_LIMIT = "10/minute" # limit to 10 requests per minute for IP
ALLOWED_SITES = [] # leave empty to allow requests from any website
OUTPUT_FORMAT = "json" # you can choose between json and xml
LANGUAGE = "en" # default output language, can be changed by request
INCLUDE_ASN = True # disable this to improve loading times (ASN is just for ISP info)