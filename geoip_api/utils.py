import socket

from ipaddress import IPv4Address, IPv6Address
from typing import Optional, Union

from geoip2.records import PlaceRecord


def get_hostname_by_addr(ip_address: Union[IPv4Address, IPv6Address]) -> Optional[str]:
    try:
        return socket.gethostbyaddr(str(ip_address))[0]
    except socket.error:
        return None


def get_localized_name(record: PlaceRecord, lang: str) -> str:
    return record.names.get(lang, record.name)
