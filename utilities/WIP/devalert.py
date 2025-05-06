import time
import json
import requests
import aya
import kismet_rest
from aya import KismetDevice


def load_macs_from_file(filename):
    with open(filename) as f:
        devs = set(f.readlines())
    return devs


def cmd_devs(devices, args):
    if len(args) == 0:
        ts = f"{(time.time() - 30):.5f}"
    elif args[0] == "all":
        ts = 0
    else:
        ts = f"{(time.time() - float(args[0])):.5f}"
    devs = activeDevices(devices, ts)
    return devs


def activeDevices(devices, fromTime) -> list[KismetDevice]:
    active_devices = devices.all(ts=fromTime)
    macs = [(aya.KismetDevice.device_from_json(i)) for i in active_devices]
    return macs


try:
    connection_parameters = aya.rest.connection_from_config(
        "./mock_data/test_connection.json"
    )
    user = connection_parameters["username"]
    passw = connection_parameters["password"]
except FileNotFoundError:
    user = "username"
    passw = "password"


devices = kismet_rest.Devices(username=user, password=passw)
devfile = "./mock_data/all-dev.txt"
soifile = "./mock_data/all-soi.txt"

target = load_macs_from_file(devfile)
targetmac = [i.split(" ")[0][:-1] for i in target]
soi = load_macs_from_file(soifile)

while True:
    soialert = []
    alert = []
    active = activeDevices(devices, 30)
    alert = list(set(active).intersection(targetmac))
    soialert = list(set(active).intersection(soi))
    if alert:
        for i in alert:
            for j in target:
                if i in j:
                    print(j)
        print("")
    if soialert:
        for i in soialert:
            print(f"#{i}")
        print("")
    if not soialert and not alert:
        print("...")
        time.sleep(2)
