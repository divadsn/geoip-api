from datetime import datetime
from typing import Optional, Union
from ipaddress import IPv4Address, IPv6Address

from pydantic import BaseModel, Field


class GeoIPCity(BaseModel):
    """Contains data for the city record associated with an IP address."""

    name: Optional[str] = Field(description="The name of the city based on the locales list passed to the constructor.")
    id: Optional[int] = Field(description="The GeoName ID for the city.")
    region: Optional[str] = Field(description="The name of the subdivision based on the locales list passed to the constructor.")
    region_code: Optional[str] = Field(description="This is a string up to three characters long contain the subdivision portion of the ISO 3166-2 code.")


class GeoIPCountry(BaseModel):
    """Contains data for the country record associated with an IP address."""

    name: Optional[str] = Field(description="The name of the country based on the locales list passed to the constructor.")
    iso_code: Optional[str] = Field(description="The two-character ISO 3166-1 alpha code for the country.")
    continent: Optional[str] = Field(description="Returns the name of the continent based on the locales list passed to the constructor.")
    continent_code: Optional[str] = Field(description="A two character continent code like “NA” (North America) or “OC” (Oceania).")
    is_eu: bool = Field(description="This is true if the country is a member state of the European Union.")


class GeoIPLocation(BaseModel):
    """Contains data for the location record associated with an IP address."""

    accuracy_radius: Optional[int] = Field(description="The approximate accuracy radius in kilometers around the latitude and longitude for the IP address.")
    zip_code: Optional[str] = Field(description="The postal code of the location.")
    latitude: Optional[float] = Field(description="The approximate latitude of the location associated with the IP address.")
    longitude: Optional[float] = Field(description="The approximate longitude of the location associated with the IP address.")
    timezone: Optional[str] = Field(description="The time zone associated with location, as specified by the IANA Time Zone Database.")


class GeoIPASN(BaseModel):
    """Contains data for the ASN record associated with an IP address."""

    name: Optional[str] = Field(description="The organization associated with the registered autonomous system number for the IP address.")
    id: Optional[int] = Field(description="The autonomous system number associated with the IP address.")


class GeoIPResponse(BaseModel):
    ip_address: Union[IPv4Address, IPv6Address] = Field(title="IP Address", description="The IP address used in the lookup.")
    hostname: Optional[str] = Field(title="Hostname", description="The hostname associated with the IP address.")
    city: GeoIPCity = Field(title="City", description="The city record associated with the IP address.")
    country: GeoIPCountry = Field(title="Country", description="The country record associated with the IP address.")
    location: GeoIPLocation = Field(title="Location", description="The location record associated with the IP address.")
    asn: Optional[GeoIPASN] = Field(title="ASN", description="The ASN record associated with the IP address.")
    last_update: datetime = Field(title="Last Update", description="The date of last GeoIP database update.")
