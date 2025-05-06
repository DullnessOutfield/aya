from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
import json
from functools import cached_property
from typing import Optional, List, Dict, Tuple, Any
from .lib import getDevs


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


@dataclass
class Survey:
    path: Path
    name: str
    location: Tuple[float, float] = field(default_factory=tuple)
    devices: List[KismetDevice] = field(default_factory=list)

    def __post_init__(self):
        if not self.name:
            self.name = self.path.stem

    def get_devices(self) -> List[KismetDevice]:
        self.devices = getDevs(self.path)

    @cached_property
    def access_points(self) -> List[KismetDevice]:
        return [
            device
            for device in self.devices
            if device.device_type in ("Wi-Fi AP", "Wi-Fi Bridged")
        ]


class Project:
    name: str
    surveys: List[Survey] = field(default_factory=list)

    @property
    def all_devices(self) -> List[KismetDevice]:
        """Get all devices across all surveys"""
        devices = []
        for survey in self.surveys:
            devices.extend(survey.devices)
        return devices


# Simple factory function to create devices from MAC addresses
def create_wifi_device(mac_address: str, **kwargs) -> WiFiDevice:
    """Create a WiFi device using a MAC address as the identifier."""
    return WiFiDevice(identifier=mac_address, **kwargs)


def create_kismet_device(mac_address: str, **kwargs) -> KismetDevice:
    """Create a Kismet device using a MAC address as the identifier."""
    return KismetDevice(identifier=mac_address, **kwargs)


def device_from_json(device_json: str) -> KismetDevice:
    data = json.loads(device_json)
    mac = data.get("kismet.device.base.macaddr")
    first_time = data.get("kismet.device.base.first_time")
    last_time = data.get("kismet.device.base.last_time")
    devtype = data.get("kismet.device.base.type")
    dev = create_kismet_device(
        mac,
        first_time=first_time,
        last_time=last_time,
        device_type=devtype,
        metadata=data,
    )
    return dev


# Test the implementation
if __name__ == "__main__":
    # Create a KismetDevice with a MAC address as the identifier
    x = create_kismet_device(
        mac_address="aabbccddeeff", name="MyDevice", device_type="Client"
    )

    print(f"x.identifier: {x.identifier}")  # This will be the MAC address
    print(f"x.identifier: {x.mac_address}")  # This will be the MAC address
