import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class KismetDevice:
    mac: str
    devtype: str
    first_time: datetime
    last_time: datetime
    json: dict
    dot11: Optional[dict] = None


class KismetdbExtractError(Exception):
    pass


def extract_json(row: tuple) -> KismetDevice:
    """
    Extracts and parses the JSON data from a Kismet database device row.
    Args:
        row (tuple): A tuple representing a row from the device table.

    Returns:
        KismetDevice: The parsed JSON data as a KismetDevice object.

    Raises:
        KismetdbExtractError: If the JSON data cannot be parsed.
    """
    row = str(row).split(",", 14)
    first_time = row[0]
    last_time = row[1]
    mac = row[4]
    devtype = row[-2]
    rawjson = row[-1]
    try:
        real_json = json.loads(rawjson[3:-2])
    except json.decoder.JSONDecodeError as e:
        raise KismetdbExtractError(f"Failed to parse device; {e}")
    if "dot11.device" in real_json.keys():
        dot11 = real_json["dot11.device"]
        return KismetDevice(mac, devtype, first_time, last_time, real_json, dot11)
    return KismetDevice(mac, devtype, first_time, last_time, real_json)


def getDevs(kismet_file: Path, devtype: list[str]) -> list[KismetDevice]:
    if type(devtype) is str:
        devtype = [devtype]
    devtype = [f"'{i}'" for i in devtype]
    con = sqlite3.connect(kismet_file)
    cur = con.cursor()
    query = f'select * from devices where type in ({', '.join(devtype)})'
    cur.execute(query)
    devs = []
    for device in cur:
        devs.append(extract_json(device))
    return devs


def getAPs(kismet_file: Path) -> list[KismetDevice]:
    """
    Get all Access Points from a kismet file
    Args:
        kismet_file (Path): The path to a kismetdb file

    Returns:
        list[dict]: A list of all the json dumps from all Wi-Fi Access Points in the db.
    """
    APs = getDevs(kismet_file, "Wi-Fi AP")
    return APs


def getSTAs(kismet_file: Path) -> list[KismetDevice]:
    STAs = getDevs(kismet_file, ["Wi-Fi Client", "Wi-Fi Device"])
    return STAs


def CheckFilepaths(Filepaths: list[Path]):
    """
    Ensures all filepaths exist
    """
    for path in Filepaths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"{path} does not exist.")


def getAPclients(device: KismetDevice) -> list:
    """
    Gets all the clients of a given Access Point
    Args:
        device (KismetDevice): The json dump of the Access Point to check

    Returns:
        list: A list of client MAC addresses
    """
    if device.dot11:
        if "dot11.device.associated_client_map" in device.dot11.keys():
            Clients = [i for i in device.dot11["dot11.device.associated_client_map"]]
            return Clients
    return []


def getBasePath() -> Path:
    home = os.path.expanduser("~")
    basepath = f"{home}/Data/"
    return Path(basepath)


def getDeviceProbeSSIDs(device: KismetDevice) -> list[str]:
    """
    Takes a kismet device json and returns all the SSIDs that device has probed for

    Args:
        device (dict): The json dump of the STA

    Returns:
        list[str]: All of the non-blank SSIDs in the device's probed_ssid_map
    """
    if device.dot11:
        if "dot11.device.probed_ssid_map" in device.dot11.keys():
            probe_map = device.dot11["dot11.device.probed_ssid_map"]
            SSIDs = [
                i["dot11.probedssid.ssid"]
                for i in probe_map
                if len(i["dot11.probedssid.ssid"]) > 0
            ]
            return SSIDs


def getDeviceConnectedAPs(device: KismetDevice) -> list[str]:
    if device.dot11 is None:
        return []
    if "dot11.device.associated_client_map" in device.dot11.keys():
        return [i for i in device.dot11["dot11.device.associated_client_map"]]
