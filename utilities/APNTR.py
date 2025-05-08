import argparse
import aya
from pathlib import Path
from aya import KismetDevice

parser = argparse.ArgumentParser()
parser.add_argument("survey", nargs="+", default="")
args = parser.parse_args()


def GetAPs(Folder: Path):
    clients: dict = {}
    for file in Folder.glob("**/*.kismet"):
        devs = aya.getSTAs(file)
        merge_project_dicts(clients, devs)
    return clients


def merge_project_dicts(master: dict, devs: list[KismetDevice]) -> dict:
    for device in devs:
        master = merge_device(master, device)
    return master


def merge_device(device_dict, device):
    mac = device.identifier
    if mac in device_dict.keys():
        device_dict[mac].extend(device.probedSSIDs)
    else:
        device_dict[mac] = device.probedSSIDs
    return device_dict


def main():
    basepath = aya.getBasePath()
    Filepaths = [(basepath / dev) for dev in args.survey]
    aya.CheckFilepaths(Filepaths)
    clients = {}

    for path in Filepaths:
        project_clients = GetAPs(path)
        for device in project_clients:
            if device in clients.keys():
                clients[device].extend(project_clients[device])
            else:
                clients[device] = project_clients[device]

    for client in clients:
        if len(clients[client]) > 1:
            print(client + ":")
            print(clients[client])


if __name__ == "__main__":
    main()
