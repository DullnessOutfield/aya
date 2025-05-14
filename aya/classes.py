from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Geolocation:
    latitude: float
    longitude: float
    altitude: float
    time: datetime


@dataclass
class Device:
    """Base class for all devices with a unique identifier."""

    identifier: str
    geolocations: List[Geolocation] = field(default_factory=list)


@dataclass
class WirelessDevice(Device):
    """Wireless device with a network address."""

    name: Optional[str] = None
    device_type: Optional[str] = None


@dataclass
class WiFiDevice(WirelessDevice):
    """WiFi device with a MAC address as its identifier."""

    @property
    def mac(self):
        return self.identifier


@dataclass
class WigleDevice(WiFiDevice):
    """
    [BSSID],[SSID],[Capabilities],[First timestamp seen],[Channel],[Frequency],[RSSI],[Latitude],[Longitude],[Altitude],[Accuracy],[RCOIs],[MfgrId],[Type]
    1a:9f:ee:5c:71:c6,Scampoodle,[WPA2-EAP-CCMP][ESS],2018-08-01 13:08:27,161,5805,-43,37.76578028,-123.45919439,67,3.2160000801086426,5A03BA0000 BAA2D00000 BAA2D02000,,WIFI
    """

    capabilities: str
    first_time: datetime
    channel: int
    frequency: int
    rssi: int
    lat: float
    lon: float
    alt: float
    accuracy: float

    # RCOI: idk,
    # MfgrId: idk
    def from_record(cls, row):
        """
        Create a WigleDevice from a row in a wiglecsv file
        """
        if isinstance(row, str):
            row = row.split(",")

        lat = row[7]
        lon = row[8]
        alt = row[9]
        first_seen = datetime.fromtimestamp(row[3])
        geolocation = Geolocation(lat, lon, alt, first_seen)

        return WigleDevice(
            identifier=row[0],
            name=row[1],
            capabilities=row[2],
            first_seen=first_seen,
            channel=row[4],
            frequency=row[5],
            rssi=row[6],
            lat=lat,
            lon=lon,
            alt=alt,
            accuracy=row[10],
            device_type="Wi-Fi AP",
            geolocations=[geolocation],
        )


# Simple factory function to create devices from MAC addresses
def create_wifi_device(mac_address: str, **kwargs) -> WiFiDevice:
    """Create a WiFi device using a MAC address as the identifier."""
    return WiFiDevice(identifier=mac_address, **kwargs)
