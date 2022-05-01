import socket

from ipaddress import IPv4Address, IPv6Address
from typing import Literal, Optional, Union

from geoip2.database import Reader
from geoip2.records import PlaceRecord

from maxminddb.reader import Metadata

# https://geoip2.readthedocs.io/en/latest/#webservices-client-api
LocaleCode = Literal["de", "en", "es", "fr", "ja", "pt-BR", "ru", "zh-CN"]


def get_hostname_by_addr(ip_address: Union[IPv4Address, IPv6Address]) -> Optional[str]:
    try:
        return socket.gethostbyaddr(str(ip_address))[0]
    except socket.error:
        return None


def get_localized_name(record: PlaceRecord, lang: str) -> str:
    return record.names.get(lang, record.name)


def get_metadata(database_file: str) -> Metadata:
    with Reader(database_file) as reader:
        return reader.metadata()
