import time
import aya
import kismet_rest
from aya import KismetDevice


def load_macs_from_file(filename):
    with open(filename) as f:
        devs = set(f.readlines())
    return devs


def activeDevices(devices, fromTime) -> list[KismetDevice]:
    fromTime = int(time.time() - float(fromTime))
    active_devices = devices.all(ts=fromTime)
    macs = [(aya.KismetDevice.from_json(i)) for i in active_devices]
    return macs


def connect_to_devices():
    try:
        connection_parameters = aya.rest.connection_from_config(
            "./mock_data/test_connection.json"
        )
        user = connection_parameters["username"]
        passw = connection_parameters["password"]
    except FileNotFoundError:
        user = "username"
        passw = "password"
    return kismet_rest.Devices(username=user, password=passw)


def main():
    devices = connect_to_devices()
    devfile = "./mock_data/all-dev.txt"
    soifile = "./mock_data/all-soi.txt"

    target = load_macs_from_file(devfile)
    targetmac = [i.split(" ")[0][:-1] for i in target]
    soi = load_macs_from_file(soifile)

    while True:
        soialert = []
        alert = []
        active = activeDevices(devices, 120)
        alert = [device for device in active if device.mac in targetmac]
        soialert = [device for device in active if device.mac in soi]
        if alert:
            for i in alert:
                print(i.identifier)
            print("")
        if soialert:
            for i in soialert:
                print(i.identifier)
            print("")
        if not soialert and not alert:
            print("...")
        time.sleep(2)


if __name__ == "__main__":
    main()
