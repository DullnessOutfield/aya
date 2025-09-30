from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from functools import cached_property
from .classes import WiFiDevice
import json


@dataclass
class KismetDevice(WiFiDevice):
    """Kismet-detected WiFi device with additional metadata."""

    first_time: Optional[datetime] = None
    last_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    dot11: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.device_type:
            self.device_type = self.device_type.strip().strip("'")

        self.dot11 = self.metadata.get("dot11.device", {})

        if not self.name:
            self.name = self.metadata.get("kismet.device.base.commonname", self.mac)

    @property
    def mac(self) -> str:
        return self.identifier

    @property
    def json(self) -> dict:
        return self.metadata
    
    @property
    def channel(self) -> str:
        return self.dot11.get('dot11.device.last_beaconed_ssid_record', {}).get('dot11.advertisedssid.channel', '')
    
    @property
    def crypt(self) -> str:
        return self.dot11.get('dot11.device.last_beaconed_ssid_record', {}).get('dot11.advertisedssid.crypt_string', '')

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
    def probehash(self):
        """A hash of the probed SSIDs to speed up comparison"""
        return hash(tuple(self.probedSSIDs))

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
    def hashes(self) -> list[str]:
        hashes = [
            str(handshake.get("dot11.eapol.rsn_pmkid"))
            for handshake in self.dot11.get("dot11.device.wpa_handshake_list", [])
            if handshake.get("dot11.eapol.rsn_pmkid")
        ]
        return hashes

    @classmethod
    def create_kismet_device(cls, mac_address: str, **kwargs):
        return KismetDevice(identifier=mac_address, **kwargs)

    @classmethod
    def from_json(cls, device_json):
        """Create a KismetDevice instance from JSON data."""
        if isinstance(device_json, str):
            data = json.loads(device_json)
        else:
            data = device_json
        data = clean_dict_keys(data)
        mac = data.get("kismet.device.base.macaddr")
        first_time = data.get("kismet.device.base.first_time")
        last_time = data.get("kismet.device.base.last_time")
        devtype = data.get("kismet.device.base.type")

        return create_kismet_device(
            mac,
            first_time=first_time,
            last_time=last_time,
            device_type=devtype,
            metadata=data,
        )


def create_kismet_device(mac_address: str, **kwargs) -> KismetDevice:
    """Create a Kismet device using a MAC address as the identifier."""
    return KismetDevice(identifier=mac_address, **kwargs)


def clean_dict_keys(obj: dict|list) -> dict:
    """
    Replace underscores with periods in dictionary keys to verify keys are consistent
    """
    if isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            new_key = key.replace('_', '.') if isinstance(key, str) else key
            # Recursively process the value
            new_dict[new_key] = clean_dict_keys(value)
        return new_dict
    elif isinstance(obj, list):
        return [clean_dict_keys(item) for item in obj]
    else:
        return obj

if __name__ == "__main__":
    x = create_kismet_device(
        mac_address="aabbccddeeff", name="MyDevice", device_type="Client"
    )
    #test later
