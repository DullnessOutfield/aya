from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional
from functools import cached_property

@dataclass
class KismetDevice:
    name: str
    mac: str
    devtype: str
    first_time: datetime
    last_time: datetime
    json: dict
    dot11: Optional[dict] = None

    def __post_init__(self):
        self.devtype = self.devtype.strip().strip("'")
        if self.dot11 is None:
            self.dot11 = {}

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
            i[1]["dot11.probedssid.ssid"]
            for i in probe_map.items()
            if len(i[1]["dot11.probedssid.ssid"]) > 0
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
        hashes = [handshake.get("dot11.eapol.rsn_pmkid") for handshake in self.dot11.get("dot11.device.wpa_handshake_list", []) if handshake.get("dot11.eapol.rsn_pmkid")]
        return hashes
