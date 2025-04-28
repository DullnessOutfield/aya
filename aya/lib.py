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





def getAPs(kismet_file: Path) -> list[dict]:
    """
    Get all Access Points from a kismet file
    Args:
        kismet_file (Path): The path to a kismetdb file

    Returns:
        list[dict]: A list of all the json dumps from all Wi-Fi Access Points in the db.
    """
    con = sqlite3.connect(kismet_file)
    cur = con.cursor()
    cur.execute("select * from devices where type == 'Wi-Fi AP'")
    APs = []
    for AP in cur:
        APs.append(extract_json(AP))
    return APs


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
    return 0


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
    return None


# x = getAPs('/home/sigsec/Data/Kismet-20250428-15-58-49-1.kismet')
# y = extract_json((1,2))
