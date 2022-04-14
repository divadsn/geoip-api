from os import path
from ipaddress import IPv4Address, IPv6Address
from typing import Optional, Union

from fastapi import APIRouter, Depends, Request, Response
from fastapi.exceptions import HTTPException
from fastapi_limiter.depends import RateLimiter

from geoip2.database import Reader
from geoip2.errors import AddressNotFoundError
from geoip2.models import City

from geoip_api.config import DEFAULT_LANGUAGE, INCLUDE_ASN, MMDB_PATH
from geoip_api.models import (
    GeoIPASN,
    GeoIPCity,
    GeoIPCountry,
    GeoIPLocation,
    GeoIPResponse,
)
from geoip_api.utils import LocaleCode, get_hostname_by_addr, get_localized_name

router = APIRouter(
    prefix="/api",
    tags=["geoip"],
    responses={
        404: {"description": "Not Found"},
        429: {"description": "Too Many Requests"},
    },
    dependencies=[
        Depends(RateLimiter(times=45, seconds=60)),
    ],
)


def _get_city_record(response: City, lang: str) -> GeoIPCity:
    return GeoIPCity(
        name=get_localized_name(response.city, lang),
        id=response.city.geoname_id,
        region=get_localized_name(response.subdivisions.most_specific, lang),
        region_code=response.subdivisions.most_specific.iso_code,
    )


def _get_country_record(response: City, lang: str) -> GeoIPCountry:
    return GeoIPCountry(
        name=get_localized_name(response.country, lang),
        iso_code=response.country.iso_code,
        continent=get_localized_name(response.continent, lang),
        continent_code=response.continent.code,
        is_eu=response.country.is_in_european_union,
    )


def _get_location_record(response: City) -> GeoIPLocation:
    return GeoIPLocation(
        accuracy_radius=response.location.accuracy_radius,
        zip_code=response.postal.code,
        latitude=response.location.latitude,
        longitude=response.location.longitude,
        timezone=response.location.time_zone,
    )


def _get_asn_record(ip_address: Union[IPv4Address, IPv6Address]) -> Optional[GeoIPASN]:
    # Check if INCLUDE_ASN is True before proceeding
    if INCLUDE_ASN:
        # Load GeoLite2 ASN database
        with Reader(path.join(MMDB_PATH, "GeoLite2-ASN.mmdb")) as reader:
            try:
                # Try to fetch data and build response, otherwise return empty
                response = reader.asn(ip_address)
                return GeoIPASN(
                    name=response.autonomous_system_organization,
                    id=response.autonomous_system_number,
                )
            except AddressNotFoundError:
                pass

    return None


@router.get("/", summary="Get GeoIP record for current IP address", response_model=GeoIPResponse)
async def get_geoip(
    request: Request, lang: Optional[LocaleCode] = None, callback: Optional[str] = None
) -> Union[GeoIPResponse, str]:
    return await get_geoip_for_ip(request.client.host, lang, callback)


@router.get("/{ip_address}", summary="Get GeoIP record for specific IP address", response_model=GeoIPResponse)
async def get_geoip_for_ip(
    ip_address: Union[IPv4Address, IPv6Address],
    lang: Optional[LocaleCode] = None,
    callback: Optional[str] = None,
) -> Union[GeoIPResponse, str]:
    # Default language if none provided
    if not lang:
        lang = DEFAULT_LANGUAGE

    # Load GeoLite2 City database
    with Reader(path.join(MMDB_PATH, "GeoLite2-City.mmdb")) as reader:
        try:
            response = reader.city(ip_address)
        except AddressNotFoundError as ex:
            raise HTTPException(status_code=404, detail=str(ex))

    # Prepare response object
    data = GeoIPResponse(
        ip_address=ip_address,
        hostname=get_hostname_by_addr(ip_address),
        city=_get_city_record(response, lang),
        country=_get_country_record(response, lang),
        location=_get_location_record(response),
        asn=_get_asn_record(ip_address),
    )

    # Return JSONP if cross-origin callback is set
    if callback:
        return Response(
            content=f"{callback}({data.json()})",
            media_type="text/javascript",
        )

    # Return built response object
    return data
