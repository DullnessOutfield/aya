from __future__ import annotations

import itertools
import json
import logging
import re
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Sequence

from .classes import BluetoothDevice, Device, WiFiDevice
from .KismetDevice import KismetDevice, create_kismet_device


def extract_json(row: tuple) -> KismetDevice:
    """Extract and parse the JSON data from a Kismet database device row.

    Args:
        row (tuple): A tuple representing a row from the device table.

    Returns:
        KismetDevice: The parsed JSON data as a KismetDevice object.

    Raises:
        JSONDecodeError: If the JSON data cannot be parsed.

    """
    first_time = datetime.fromtimestamp(int(row[0]), UTC)
    last_time = datetime.fromtimestamp(int(row[1]), UTC)
    mac: str = row[4]
    devtype: str = row[13]
    rawjson: str = row[14]
    try:
        real_json: dict = json.loads(rawjson)
    except json.decoder.JSONDecodeError as e:
        real_json = {}
        logging.warning("Error decoding %s: %s", mac, e)
    return create_kismet_device(
        mac,
        first_time=first_time,
        last_time=last_time,
        device_type=devtype,
        metadata=real_json,
    )


def get_devs(
    kismet_file: Path, devtype: list[str] | None = None,
) -> list[KismetDevice]:
    """Get devices from a kismet file.

    Args:
        kismet_file (Path): The path to a kismetdb file
        devtype (Optional list[str]): kismetdb device types to pull. Will pull all devices if not provided.

    Returns:
        list[dict]: A list of all the json dumps from all Wi-Fi Access Points in the db.

    Raises:
        FileNotFoundError: if kismet_file does not exist
        sqlite3.OperationalError: If the query fails for whatever reason

    """
    if not Path.exists(kismet_file):
        msg = f"File not found: {kismet_file}"
        raise FileNotFoundError(msg)
    if isinstance(devtype, str):
        devtype = [devtype]
    if devtype is None:
        devtype = ["all"]
    devtype = [f"'{i}'" for i in devtype]
    con = sqlite3.connect(kismet_file)
    cur = con.cursor()
    if devtype == ["'all'"]:
        query = "select * from devices"
    else:
        query = f"select * from devices where type in ({', '.join(devtype)})"
    cur.execute(query)
    devs = []
    for device in cur:
        dev = extract_json(device)
        if dev:
            devs.append(dev)
    return devs


def get_access_points(kismet_file: Path) -> list[KismetDevice]:
    """Get all Access Points from a kismet file.

    Args:
        kismet_file (Path): The path to a kismetdb file

    Returns:
        list[dict]: A list of all the json dumps from all Wi-Fi Access Points in the db.

    """
    return get_devs(kismet_file, ["Wi-Fi AP", "Wi-Fi Bridged"])


def get_stas(kismet_file: Path) -> list[KismetDevice]:
    """Get all Wi-Fi Devices/Clients from a kismet file.

    Args:
        kismet_file (Path): The path to a kismetdb file

    Returns:
        list[dict]: A list of all the json dumps from all Wi-Fi STAs in the db.

    """
    return get_devs(kismet_file, ["Wi-Fi Client", "Wi-Fi Device"])


def check_filepaths(filepaths: list[Path]) -> None:
    """Ensure all filepaths exist.

    Args:
        filepaths (list[Path]): A list of file paths to check.

    """
    for path in filepaths:
        if not Path.exists(path):
            raise FileNotFoundError(path)


def get_basepath() -> Path:
    """Retrieve folder where Projects live.

    Defaults to ~/Data, otherwise checks pathconfig.txt for a single line containing an alternate path.

    Returns:
        Path: folder which should contain Projects

    """
    pathfile = Path("./pathconfig.txt")
    if Path.exists(pathfile):
        with Path.open(pathfile) as f:
            configured_path = Path(f.readline())
        if Path.exists(configured_path):
            return Path(configured_path)
    home = Path.expanduser(Path("~"))
    basepath = f"{home}/Data/"
    return Path(basepath)


def find_soi(kismet_file: Path, targets: Sequence[Device]) -> list[KismetDevice | BluetoothDevice]:
    """Find devices of interest in a Kismet database file.

    Supports MAC and SSID matching.

    Args:
        kismet_file (Path): The path to the Kismet database file.
        targets (Sequence[Device]): A sequence of `Device` objects to search for.

    Returns:
        list[KismetDevice]: A list of `KismetDevice` matches

    Raises:
        FileNotFoundError: If the specified Kismet database file does not exist.

    """
    if not Path.exists(kismet_file):
        msg = f"File not found: {kismet_file}"
        raise FileNotFoundError(msg)
    wifi_targets: list[WiFiDevice] = [i for i in targets if isinstance(i, WiFiDevice)]
    bt_targets: list[str] = [i.identifier for i in targets if isinstance(i, BluetoothDevice)]
    target_macs = [i.mac for i in wifi_targets]
    target_ssids = [i.name for i in wifi_targets]
    try:
        devices = get_devs(kismet_file)
    except sqlite3.OperationalError:
        devices = []
    bt_hits = [i for i in devices if i.mac in bt_targets]
    mac_hits = [i for i in devices if i.mac in target_macs]
    aps = [i for i in devices if i.device_type == "Wi-Fi AP"]
    ssid_hits = [i for i in aps if i.name in target_ssids]
    return list(mac_hits + ssid_hits + bt_hits)


def find_oui_matches(kismet_file: Path, oui_list: list[str]) -> list[KismetDevice]:
    """Get all devices matching given OUIs.

    Args:
        kismet_file (Path): kismetdb to pull devices from
        oui_list (list[str]): list of MAC addresses or OUIs to be matched to

    Returns:
        list[KismetDevice]: Matching devices

    Raises:
        FileNotFoundError: if kismet_file does not exist
        sqlite3.OperationalError: if query fails to run

    """
    if not Path.exists(kismet_file):
        msg = f"File not found: {kismet_file}"
        raise FileNotFoundError(msg)
    oui_list = [f'"{clean_oui(i)}"' for i in oui_list]
    oui_joined = ", ".join(oui_list)
    con = sqlite3.connect(kismet_file)
    cur = con.cursor()
    query = f"select * from devices where substr(devmac,1,8) in ({oui_joined})"
    try:
        cur.execute(query)
    except sqlite3.OperationalError as e:
        raise e
    devs = []
    for device in cur:
        devs.append(extract_json(device))
    return devs


def clean_oui(oui: str) -> str:
    """Take a MAC or OUI fragment and return it in a standard format.

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
    oui_pairs = [oui[i : i + 2] for i in range(0, 6, 2)]
    return ":".join(oui_pairs).upper()


def generate_24g_channels():
    """Get dict containing center freq / freq ranges for all 14 2.4GHz wifi channels."""
    channel_map = {}
    for i in range(1, 14):
        freq = 2407 + (i * 5)
        freqwidth = 11
        channel_map[i] = {"center": freq, "range": [freq - freqwidth, freq + freqwidth]}
    return channel_map


def generate_5g_channels():
    """Get dict containing center freq / freq ranges for all 5GHz wifi channels."""
    channelwidths = [
        [[180, 182, 184, 187, 189], 10],
        [[34, 38, 46, 54, 62, 102, 110, 118, 126, 134, 142, 151, 159, 167, 175], 40],
        [[42, 58, 106, 122, 138, 155, 171], 80],
        [[50, 114, 163], 160],
    ]

    channelwidths.append(
        [
            [
                i
                for i in range(200)
                if i
                not in list(
                    itertools.chain(
                        channelwidths[0][0],
                        channelwidths[1][0],
                        channelwidths[2][0],
                        channelwidths[3][0],
                    )
                )
            ],
            20,
        ]
    )
    for i in channelwidths:
        print(i)

    channel_map = {}
    for i in range(200):
        freq = (i * 5) + 5000
        freqwidth = 0
        for channelwidth in channelwidths:
            if i in channelwidth[0]:
                freqwidth = int(channelwidth[1] * 0.5)
                channel_map[i] = {
                    "center": freq,
                    "range": [freq - freqwidth, freq + freqwidth],
                }
                break
    return channel_map


def get_freq_data(kismet_file: Path):
    """Calculate how many packets occurred on each Wi-Fi channel."""
    freqcount = {}
    con = sqlite3.connect(kismet_file)
    cur = con.cursor()
    for j in cur.execute(
        "select frequency, count(frequency) from packets where frequency > 0 group by frequency"
    ):
        j: list[int] = list(j)
        j[0] = int(j[0] * (10**-3))
        if j[0] not in freqcount:
            freqcount[j[0]] = j[1]
        else:
            freqcount[j[0]] += j[1]
    return freqcount


def channel_count(kismet_file: Path):
    MAX_24G_FREQ = 3000
    freqcount = get_freq_data(kismet_file)
    channel_map_5g = generate_5g_channels()
    channel_map_24g = generate_24g_channels()
    channel_map = {}

    for channel in channel_map_5g.values():
        for k,v in freqcount.items():
            if channel["center"] == k:
                channel_map[channel] = v
            else:
                channel_map[channel] = 0

    for j in freqcount:
        if j < MAX_24G_FREQ:
            for channel in channel_map_24g:
                if channel_map_24g[channel]["center"] == j:
                    channel_map[channel] = freqcount[j]
    return channel_map

