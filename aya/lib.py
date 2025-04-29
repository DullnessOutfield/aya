import sqlite3
import json
import os
import re
from pathlib import Path
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
    name = real_json["kismet.device.base.commonname"]
    if "dot11.device" in real_json.keys():
        dot11 = real_json["dot11.device"]
        return KismetDevice(name, mac, devtype, first_time, last_time, real_json, dot11)
    return KismetDevice(name, mac, devtype, first_time, last_time, real_json)


def getDevs(kismet_file: Path, devtype: list[str] = []) -> list[KismetDevice]:
    """
    Get devices from a kismet file
    Args:
        kismet_file (Path): The path to a kismetdb file
        devtype (Optional list[str]): kismetdb device types to pull. Will pull all devices if not provided.

    Returns:
        list[dict]: A list of all the json dumps from all Wi-Fi Access Points in the db.
    """
    if type(devtype) is str:
        devtype = [devtype]
    devtype = [f"'{i}'" for i in devtype]
    con = sqlite3.connect(kismet_file)
    cur = con.cursor()
    if not devtype or devtype == ["'all'"]:
        query = 'select * from devices'
    else:
        query = f'select * from devices where type in ({', '.join(devtype)})'
    cur.execute(query)
    devs = []
    for device in cur:
        try:
            devs.append(extract_json(device))
        except:
            pass
    return devs


def getAPs(kismet_file: Path) -> list[KismetDevice]:
    """
    Get all Access Points from a kismet file
    Args:
        kismet_file (Path): The path to a kismetdb file

    Returns:
        list[dict]: A list of all the json dumps from all Wi-Fi Access Points in the db.
    """
    APs = getDevs(kismet_file, ["Wi-Fi AP", 'Wi-Fi Bridged'])
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
    pathfile = './pathconfig.txt'
    if os.path.exists(pathfile):
        with open(pathfile) as f:
            configured_path = f.readline()
        if os.path.exists(configured_path):
            return Path(configured_path)
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
                i[1]["dot11.probedssid.ssid"]
                for i in probe_map.items()
                if len(i[1]["dot11.probedssid.ssid"]) > 0
            ]
            return SSIDs
    return []


def getDeviceConnectedAPs(device: KismetDevice) -> list[str]:
    """
    Pulls any APs a device connected to during a survey
    Args:
        device (KismetDevice): The device to check

    Returns:
        list[str]: MAC addresses of all connected access points
    """
    if device.dot11 is not None:
        if "dot11.device.associated_client_map" in device.dot11.keys():
            return [i for i in device.dot11["dot11.device.associated_client_map"]]
    return []

def findOUIMatches(kismet_file: Path, OUI_list: list[str]) -> list[KismetDevice]:
    """
    Gets all devices matching given OUIs
    Args:
        kismet_file (Path): kismetdb to pull devices from
        OUI_list (list[str]): list of MAC addresses or OUIs to be matched to
    Returns:
        list[KismetDevice]: Matching devices
    """
    OUI_list = [clean_OUI(i) for i in OUI_list]
    OUI_list = ', '.join(OUI_list)
    con = sqlite3.connect(kismet_file)
    cur = con.cursor()
    query = f'select * from devices where substr(devmac,1,8) in ({OUI_list})'
    cur.execute(query)
    devs = []
    for device in cur:
        devs.append(extract_json(device))
    return devs

def clean_OUI(oui: str) -> str:
    """
    Takes a MAC or OUI fragment and returns it in a standard format
    Args:
        oui (str): A MAC addr or OUI
    Returns:
        str: Standard OUI formatted as AA:BB:CC
        '': Returns empty string if given mutilated str
    """
    oui = re.sub(r'[^0-9a-fA-F]', '', oui)
    oui = oui[:6]
    if len(oui) != 6:
        return ''
    oui = [oui[i:i+2] for i in range(0,6,2)]
    return ':'.join(oui).upper()