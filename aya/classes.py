from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


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


@dataclass
class KismetDevice(WiFiDevice):
    """Kismet-detected WiFi device with additional metadata."""

    first_time: Optional[datetime] = None
    last_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    dot11: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Clean up device type formatting."""
        if self.device_type:
            self.device_type = self.device_type.strip().strip("'")
        self.dot11 = self.metadata.get("dot11.device", {})
        self.name = self.metadata.get("kismet.device.base.commonname", self.mac)


# Simple factory function to create devices from MAC addresses
def create_wifi_device(mac_address: str, **kwargs) -> WiFiDevice:
    """Create a WiFi device using a MAC address as the identifier."""
    return WiFiDevice(identifier=mac_address, **kwargs)
