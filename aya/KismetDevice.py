from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class KismetDevice:
    name: str
    mac: str
    devtype: str
    first_time: datetime
    last_time: datetime
    json: dict
    dot11: Optional[dict] = None

    def getDeviceProbeSSIDs(self) -> list[str]:
        """
        Takes a kismet device json and returns all the SSIDs that device has probed for

        Args:
            device (dict): The json dump of the STA

        Returns:
            list[str]: All of the non-blank SSIDs in the device's probed_ssid_map
        """

        probe_map = self.dot11.get("dot11.device.probed_ssid_map")
        SSIDs = [
            i[1]["dot11.probedssid.ssid"]
            for i in probe_map.items()
            if len(i[1]["dot11.probedssid.ssid"]) > 0
        ]
        return SSIDs

    def getAPclients(self) -> list:
        """
        Gets all the clients of a given Access Point
        Args:
            device (KismetDevice): The json dump of the Access Point to check

        Returns:
            list: A list of client MAC addresses
        """
        Clients = [i for i in self.dot11.get("dot11.device.associated_client_map")]
        return Clients

    def getDeviceConnectedAPs(self) -> list[str]:
        """
        Pulls any APs a device connected to during a survey
        Args:
            device (KismetDevice): The device to check

        Returns:
            list[str]: MAC addresses of all connected access points
        """
        return [i for i in self.dot11.get("dot11.device.associated_client_map")]

    def getHashes(self) -> str:
        for handshake in self.dot11.get("dot11.device.wpa_handshake_list"):
            return handshake.get("dot11.eapol.rsn_pmkid")
