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

    capabilities: str = field(default="")
    first_time: Optional[datetime] = None
    channel: int = 0
    frequency: int = 0
    rssi: int = 0
    lat: float = 0.0
    lon: float = 0.0
    alt: float = 0.0
    accuracy: float = 0.0

    def __post_init__(self):
        if not self.name:
            self.name = self.identifier

    @property
    def mac(self) -> str:
        """Return the MAC address (identifier)."""
        return self.identifier

    @property
    def location(self) -> Optional[Geolocation]:
        """Return the most recent geolocation if available."""
        if self.geolocations:
            return self.geolocations[-1]
        return None

    @classmethod
    def from_record(self, row):
        """
        Create a WigleDevice from a row in a wiglecsv file
        """
        if isinstance(row, str):
            row = row.split(",")

        lat = row[7]
        lon = row[8]
        alt = row[9]
        first_seen = datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S')
        geolocation = Geolocation(lat, lon, alt, first_seen)
        return create_wigle_device(
            mac_address=row[0],
            name=row[1],
            capabilities=row[2],
            first_time=first_seen,
            channel=int(row[4]) if row[4] else 0,
            frequency=int(row[5]) if row[5] else 0,
            rssi=int(row[6]) if row[6] else 0,
            lat=lat,
            lon=lon,
            alt=alt,
            accuracy=float(row[10]) if row[10] else 0.0,
            device_type="Wi-Fi AP",
            geolocations=[geolocation],
        )


# Simple factory function to create devices from MAC addresses
def create_wifi_device(mac_address: str, **kwargs) -> WiFiDevice:
    """Create a WiFi device using a MAC address as the identifier."""
    return WiFiDevice(identifier=mac_address, **kwargs)


def create_wigle_device(mac_address: str, **kwargs) -> WigleDevice:
    """Create a Wigle device using a MAC address as the identifier."""
    return WigleDevice(identifier=mac_address, **kwargs)
