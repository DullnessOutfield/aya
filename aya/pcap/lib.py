from __future__ import annotations

import binascii
from pathlib import Path

import pyshark
from pyshark.packet.packet import Packet

from aya.classes import WiFiDevice

fc_types = {
    8: "DATA_TYPE",
    36: "TRIGGER_TYPE",
    64: "PROBE_REQ_TYPE",
    72: "NULL_TYPE",
    80: "PROBE_RESP_TYPE",
    84: "VHT_NDP_TYPE",
    128: "BEACON_TYPE",
    136: "QOS_DATA_TYPE",
    148: "BLOCK_ACK_TYPE",
    180: "RTS_TYPE",
    200: "QOS_NULL_TYPE",
    208: "ACTION_TYPE",
    224: "NO_ACK_TYPE",
}
ap_types = ["BEACON_TYPE", "PROBE_RESP_TYPE"]


def hex_to_ascii(hex_string: str) -> str:
    """Translate pyshark hex data into text."""
    try:
        return binascii.unhexlify(hex_string.replace(":", "")).decode("ascii", errors="ignore")
    except binascii.Error:
        return hex_string


def get_ssid_from_packet(packet: Packet) -> str:
    """Get SSID from packet if it exists."""
    if hasattr(packet, "wlan.mgt"):
        ssid = packet["wlan.mgt"].get("wlan_ssid", "")
        return "" if ssid == "SSID: <MISSING>" else hex_to_ascii(ssid)
    return ""


def wifi_device_from_packet(packet: Packet) -> WiFiDevice:
    """Create an Aya WiFi>Device from a pyshark Packets."""
    dev_type = None
    ssid = None
    if packet.wlan.fc_type_subtype.hex_value in fc_types:
        fc_type = fc_types[packet.wlan.fc_type_subtype.hex_value]
        if fc_type in ap_types:
            dev_type = "Wi-Fi AP"
            ssid = get_ssid_from_packet(packet)

    return WiFiDevice(packet.wlan.ta, [], dev_type, ssid)


def get_devs(filename: Path) -> list[WiFiDevice]:
    """Generate a list of Aya WiFIDevices from a pcap."""
    devs: dict[str, WiFiDevice] = {}
    capture: pyshark.FileCapture = pyshark.FileCapture(filename)
    for packet in capture:
        if hasattr(packet.wlan, "ta"):
            mac = packet.wlan.ta
            if mac not in devs:
                devs[mac] = wifi_device_from_packet(packet)
                print(devs[mac])
    return list(devs.values())


devices = get_devs(Path("/home/sigsec/courtyardusm.pcap"))
for i in devices:
    print(i)
