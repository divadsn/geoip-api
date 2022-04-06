import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/")
MMDB_PATH = os.getenv("MMDB_PATH", "/usr/share/GeoIP")
RATE_LIMIT = os.getenv("RATE_LIMIT", "10/minute")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")
INCLUDE_ASN = os.getenv("INCLUDE_ASN", "True").lower() in ("yes", "true", "t", "1")
