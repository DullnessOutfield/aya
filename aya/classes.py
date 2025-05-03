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

    # No new fields, the MAC is the identifier


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


# Simple factory function to create devices from MAC addresses
def create_wifi_device(mac_address: str, **kwargs) -> WiFiDevice:
    """Create a WiFi device using a MAC address as the identifier."""
    return WiFiDevice(identifier=mac_address, **kwargs)


def create_kismet_device(mac_address: str, **kwargs) -> KismetDevice:
    """Create a Kismet device using a MAC address as the identifier."""
    return KismetDevice(identifier=mac_address, **kwargs)


# Test the implementation
if __name__ == "__main__":
    # Create a KismetDevice with a MAC address as the identifier
    x = create_kismet_device(
        mac_address="aabbccddeeff", name="MyDevice", device_type="Client"
    )

    print(f"x.identifier: {x.identifier}")  # This will be the MAC address
    print(f"x.identifier: {x.mac_address}")  # This will be the MAC address
