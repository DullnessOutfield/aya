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
        file_dict: dict = parseKismetdb(file, clients)
        merge_dicts(clients, file_dict)
    return clients


def parseKismetdb(file: Path, file_dict: dict) -> dict:
    devs = aya.getSTAs(file)
    for dev in devs:
        file_dict = merge_device(file_dict, dev)
    return file_dict

def merge_dicts(master: dict, new: dict) -> dict:
    for name,entry in new.items():
        probes = entry['Probes']
        APs = entry['APs']
        master = merge_entry(master,name,probes,APs)
    return master

def merge_device(clients: dict, device: KismetDevice):
    probes: list[str] = device.probedSSIDs
    connected_APs: list[str] = device.clients
    name = device.name
    merge_entry(clients,name,probes,connected_APs)
    return clients

def merge_entry(master: dict, name, probes, connected_APs) -> dict:
    if name in master.keys():
        master[name]["Probes"].extend(probes)
        master[name]["APs"].extend(connected_APs)
        master[name]["Probes"] = list(set(master[name]["Probes"]))
        master[name]["APs"] = list(set(master[name]["APs"]))
    else:
        master[name] = {"APs": connected_APs, "Probes": probes}
    return master


def main():
    basepath = aya.getBasePath()
    Filepaths = [(basepath / dev) for dev in args.survey]
    aya.CheckFilepaths(Filepaths)

    for path in Filepaths:
        clients = GetAPs(path)

    for client in clients:
        if len(clients[client]["Probes"]) > 1:
            print(client + ":")
            print(clients[client]["Probes"])

if __name__ == "__main__":
    main()
