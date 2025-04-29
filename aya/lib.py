import sqlite3
import json
import os
from pathlib import Path


class KismetdbExtractError(Exception):
    pass



def extract_json(row: tuple) -> dict:
    """
    Extracts and parses the JSON data from a Kismet database device row.
    Args:
        row (tuple): A tuple representing a row from the device table.

    Returns:
        dict: The parsed JSON data as a dictionary.

    Raises:
        KismetdbExtractError: If the JSON data cannot be parsed.
    """
    rawjson = str(row).split(",", 14)[-1]
    try:
        real_json = json.loads(rawjson[3:-2])
    except json.decoder.JSONDecodeError as e:
        raise KismetdbExtractError(f"Failed to parse device; {e}")
    return real_json



def getDevs(kismet_file: Path, devtype: list[str]) -> list[dict]:
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

def getAPs(kismet_file: Path) -> list[dict]:
    """
    Get all Access Points from a kismet file
    Args:
        kismet_file (Path): The path to a kismetdb file

    Returns:
        list[dict]: A list of all the json dumps from all Wi-Fi Access Points in the db.
    """
    APs = getDevs(kismet_file, 'Wi-Fi AP')
    return APs

def getSTAs(kismet_file: Path) -> list[dict]:
    STAs = getDevs(kismet_file, ['Wi-Fi Client', 'Wi-Fi Device'])
    return STAs
    
def CheckFilepaths(Filepaths: list[Path]):
    """
    Ensures all filepaths exist
    Args:
        filepaths (list[Path]): The filepaths to check

    Raises:
        FileNotFoundError: If one path doesn't exist
    """
    for path in Filepaths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"{path} does not exist.")


def getAPclients(device: dict) -> list:
    """
    Gets all the clients of a given Access Point
    Args:
        device (dict): The json dump of the Access Point to check
    
    Returns:
        list: A list of client MAC addresses
    """
    if "dot11.device" in device.keys():
        if "dot11.device.associated_client_map" in device["dot11.device"].keys():
            Clients = [i for i in device["dot11.device"]["dot11.device.associated_client_map"]]
            return Clients
    return []

def getBasePath() -> Path:
    home = os.path.expanduser("~")
    basepath = f"{home}/Data/"
    return Path(basepath)

def getDeviceProbeSSIDs(device: dict) -> list[str]:
    """
    Takes a kismet device json and returns all the SSIDs that device has probed for
    
    Args:
        device (dict): The json dump of the STA

    Returns:
        list[str]: All of the non-blank SSIDs in the device's probed_ssid_map
    """
    if 'dot11.device' in device.keys():
        if 'dot11.device.probed_ssid_map' in device["dot11.device"].keys():
            probe_map = device["dot11.device"]["dot11.device.probed_ssid_map"]
            SSIDs = [i["dot11.probedssid.ssid"] for i in probe_map if len(i["dot11.probedssid.ssid"]) > 0]
            return SSIDs

def getDeviceConnectedAPs(device: dict) -> list[str]:
    #TODO
    return 0