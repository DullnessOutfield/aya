from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from functools import cached_property
from .classes import WiFiDevice


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

    @property
    def mac(self) -> str:
        return self.identifier

    @property
    def json(self) -> dict:
        return self.metadata

    @cached_property
    def probedSSIDs(self) -> list[str]:
        """
        Takes a kismet device json and returns all the SSIDs that device has probed for

        Args:
            device (dict): The json dump of the STA

        Returns:
            list[str]: All of the non-blank SSIDs in the device's probed_ssid_map
        """

        probe_map = self.dot11.get("dot11.device.probed_ssid_map", {})
        SSIDs = [
            i["dot11.probedssid.ssid"]
            for i in probe_map
            if len(i["dot11.probedssid.ssid"]) > 0
        ]
        return SSIDs

    @cached_property
    def clients(self) -> list[str]:
        """
        Gets all the clients of a given Access Point
        Args:
            device (KismetDevice): The json dump of the Access Point to check

        Returns:
            list: A list of client MAC addresses
        """
        return [i for i in self.dot11.get("dot11.device.associated_client_map", {})]

    @cached_property
    def hashes(self) -> str:
        hashes = [
            handshake.get("dot11.eapol.rsn_pmkid")
            for handshake in self.dot11.get("dot11.device.wpa_handshake_list", [])
            if handshake.get("dot11.eapol.rsn_pmkid")
        ]
        return hashes


def create_kismet_device(mac_address: str, **kwargs) -> KismetDevice:
    """Create a Kismet device using a MAC address as the identifier."""
    return KismetDevice(identifier=mac_address, **kwargs)
