import sqlite3
import json
import os
import re
import logging
import itertools
from pathlib import Path
from datetime import datetime
from .KismetDevice import KismetDevice, create_kismet_device


def extract_json(row: tuple) -> KismetDevice:
    """
    Extracts and parses the JSON data from a Kismet database device row.
    Args:
        row (tuple): A tuple representing a row from the device table.

    Returns:
        KismetDevice: The parsed JSON data as a KismetDevice object.

    Raises:
        JSONDecodeError: If the JSON data cannot be parsed.
    """

    first_time = datetime.fromtimestamp(int(row[0]))
    last_time = datetime.fromtimestamp(int(row[1]))
    mac = row[4]
    devtype = row[13]
    rawjson = row[14]
    try:
        real_json = json.loads(rawjson)
    except json.decoder.JSONDecodeError as e:
        real_json = {}
        logging.warning(f"Error decoding {mac}: {e}")
    dev = create_kismet_device(
        mac,
        first_time=first_time,
        last_time=last_time,
        device_type=devtype,
        metadata=real_json,
    )
    return dev


def getDevs(kismet_file: Path, devtype: list[str] = []) -> list[KismetDevice]:
    """
    Get devices from a kismet file
    Args:
        kismet_file (Path): The path to a kismetdb file
        devtype (Optional list[str]): kismetdb device types to pull. Will pull all devices if not provided.

    Returns:
        list[dict]: A list of all the json dumps from all Wi-Fi Access Points in the db.

    Raises:
        FileNotFoundError: if kismet_file does not exist
        sqlite3.OperationalError: If the query fails for whatever reason
    """
    if not os.path.exists(kismet_file):
        raise FileNotFoundError(f"File not found: {kismet_file}")
    if type(devtype) is str:
        devtype = [devtype]
    devtype = [f"'{i}'" for i in devtype]
    con = sqlite3.connect(kismet_file)
    cur = con.cursor()
    if not devtype or devtype == ["'all'"]:
        query = "select * from devices"
    else:
        query = f"select * from devices where type in ({', '.join(devtype)})"
    try:
        cur.execute(query)
    except sqlite3.OperationalError as e:
        raise e
    devs = []
    for device in cur:
        try:
            dev = extract_json(device)
            devs.append(dev)
        except json.decoder.JSONDecodeError as e:
            logging.warning(f"Error decoding device: {e}")
    return devs


def getAPs(kismet_file: Path) -> list[KismetDevice]:
    """
    Get all Access Points from a kismet file
    Args:
        kismet_file (Path): The path to a kismetdb file

    Returns:
        list[dict]: A list of all the json dumps from all Wi-Fi Access Points in the db.
    """
    APs = getDevs(kismet_file, ["Wi-Fi AP", "Wi-Fi Bridged"])
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


def getBasePath() -> Path:
    pathfile = "./pathconfig.txt"
    if os.path.exists(pathfile):
        with open(pathfile) as f:
            configured_path = f.readline()
        if os.path.exists(configured_path):
            return Path(configured_path)
    home = os.path.expanduser("~")
    basepath = f"{home}/Data/"
    return Path(basepath)

def find_soi(kismet_file: Path, soi_file: Path) -> list[KismetDevice]:
    if not os.path.exists(kismet_file):
        raise FileNotFoundError(f"File not found: {kismet_file}")
    with open(soi_file) as f:
        soi_list = f.readlines()
    soi_list = ', '.join([f'"{i.upper().strip()}"' for i in soi_list if i.strip()])
    con = sqlite3.connect(kismet_file)
    cur = con.cursor()
    query = f"select * from devices where devmac in ({soi_list})"
    try:
        cur.execute(query)
    except sqlite3.OperationalError as e:
        raise e
    devs = []
    for device in cur:
        devs.append(extract_json(device))
    return devs


def findOUIMatches(kismet_file: Path, OUI_list: list[str]) -> list[KismetDevice]:
    """
    Gets all devices matching given OUIs
    Args:
        kismet_file (Path): kismetdb to pull devices from
        OUI_list (list[str]): list of MAC addresses or OUIs to be matched to
    Returns:
        list[KismetDevice]: Matching devices
    Raises:
        FileNotFoundError: if kismet_file does not exist
        sqlite3.OperationalError: if query fails to run
    """
    if not os.path.exists(kismet_file):
        raise FileNotFoundError(f"File not found: {kismet_file}")
    OUI_list = [f'"{clean_OUI(i)}"' for i in OUI_list]
    OUI_list = ", ".join(OUI_list)
    con = sqlite3.connect(kismet_file)
    cur = con.cursor()
    query = f"select * from devices where substr(devmac,1,8) in ({OUI_list})"
    try:
        cur.execute(query)
    except sqlite3.OperationalError as e:
        raise e
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
    oui = re.sub(r"[^0-9a-fA-F]", "", oui)
    oui = oui[:6]
    if len(oui) != 6:
        return ""
    oui = [oui[i : i + 2] for i in range(0, 6, 2)]
    return ":".join(oui).upper()

def Generate24GChannels():
    channel_map = {}
    for i in range(1,14):
        freq = 2407+(i*5)
        freqwidth = 11
        channel_map[i] = {"center":freq, "range":[freq-freqwidth,freq+freqwidth]}
    return channel_map

def Generate5GChannels():
    channelwidths=[[[180, 182, 184, 187, 189],10],\
                   [[34, 38, 46, 54, 62, 102, 110, 118, 126, 134, 142, 151, 159, 167, 175],40],\
                   [[42, 58, 106, 122, 138, 155, 171],80],\
                   [[50, 114, 163],160]]

    channelwidths.append([[i for i in range(200)\
                          if i not in\
                          list(itertools.chain(channelwidths[0][0]\
                                               ,channelwidths[1][0]\
                                               ,channelwidths[2][0]\
                                               ,channelwidths[3][0]))],20])
    for i in channelwidths:
        print(i)
    

    channel_map = {}
    for i in range(200):
        freq = (i*5)+5000
        for channelwidth in channelwidths:
            if i in channelwidth[0]:
                freqwidth = int(channelwidth[1]*.5)
        channel_map[i] = {"center":freq, "range":[freq-freqwidth,freq+freqwidth]}
        #print(i,freq)
    return channel_map

def get_freq_data(kismet_file: Path):
    freqcount = {}
    con = sqlite3.connect(kismet_file)
    cur = con.cursor()
    for j in cur.execute('select frequency, count(frequency) from packets where frequency > 0 group by frequency'):
        j = list(j)
        j[0] = int(j[0]*(10**-3))
        if j[0] not in freqcount:
            freqcount[j[0]] = j[1]
        else:
            freqcount[j[0]] += j[1]
    return freqcount

def channel_count(kismet_file: Path):
    freqcount = get_freq_data(kismet_file)
    channelmap5G = Generate5GChannels()
    channelmap24G = Generate24GChannels()
    channel_map = {}


    for channel in channelmap5G:
        for i in freqcount:
            if channelmap5G[channel]['center'] == i:
                channel_map[channel] = freqcount[i]
        else:
            channel_map[channel] = 0
                
    for i,j in enumerate(freqcount):
        if j < 3000:
            for channel in channelmap24G:
                if channelmap24G[channel]['center'] == j:
                    channel_map[channel] = freqcount[j]
    return channel_map