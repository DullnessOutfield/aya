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
    device_type: Optional[str] = None


@dataclass
class LicensePlate(Device):
    """Experimental License Plate class for ALPR"""

    state: Optional[str] = None
    registration: Optional[str] = None


@dataclass
class WirelessDevice(Device):
    """Wireless device with a network address."""

    name: Optional[str] = None


@dataclass
class TPMSDevice(WirelessDevice):
    """Tire Pressure Sensor device"""

    data: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.device_type:
            self.device_type = "TPMS"


@dataclass
class RFIDDevice(WirelessDevice):
    """RFID device"""

    def __post_init__(self):
        if not self.device_type:
            self.device_type = "RFID"


@dataclass
class BluetoothDevice(WirelessDevice):
    """Bluetooth device with a MAC address as its identifier."""

    def __post_init__(self):
        if not self.device_type:
            self.device_type = "Bluetooth"

    @property
    def mac(self):
        return self.identifier


@dataclass
class WiFiDevice(WirelessDevice):
    """WiFi device with a MAC address as its identifier."""

    @property
    def mac(self):
        return self.identifier


@dataclass
class WigleDevice(WiFiDevice):
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
    def from_record(cls, row):
        """
        Create a WigleDevice from a row in a wiglecsv file
        """
        if isinstance(row, str):
            row = row.split(",")

        lat: float = float(row[7])
        lon: float = float(row[8])
        alt: float = float(row[9])
        first_seen = datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")
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
