from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Geolocation:
    latitude: float
    longitude: float
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


# Simple factory function to create devices from MAC addresses
def create_wifi_device(mac_address: str, **kwargs) -> WiFiDevice:
    """Create a WiFi device using a MAC address as the identifier."""
    return WiFiDevice(identifier=mac_address, **kwargs)
