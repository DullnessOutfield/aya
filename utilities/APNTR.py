import argparse
import csv
import aya
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("survey", nargs='+', default="")
args = parser.parse_args()

Clients = {}

def GetAPs(Folder: Path):
    for file in Folder.glob('**/*.kismet'):
        parseKismetdb(file)
    
    for file in Folder.glob('**/Kismet/**/*.csv'):
        parseAirodump(file)
                                        

def parseAirodump(file: Path):
    with open(file) as csvfile:
        sheet = csv.reader(csvfile)
        for dev in sheet:
            if len(dev):
                SSID = dev[0]
                Probes = dev[13:]
                if SSID not in Clients:
                    Clients[SSID] = {"APs": [], "Probes": []}
                for probe in Probes:
                    if probe not in Clients[SSID]['Probes'] and probe != ' ':
                        Clients[SSID]['Probes'].append(probe)

def parseKismetdb(file: Path) -> dict:
    file_dict = {}
    devs = aya.getSTAs(file)
    for dev in devs:
        SSID = dev["kismet.device.base.commonname"]
        probes: list[str] = aya.getDeviceProbeSSIDs(dev)
        connected_APs: list[str] = aya.getDeviceConnectedAPs(dev)
        if SSID in file_dict.keys():
            file_dict[SSID]['Probes'].extend(probes)
            file_dict[SSID]['APs'].extend(connected_APs)
            file_dict[SSID]['Probes'] = list(set(file_dict[SSID]['Probes']))
            file_dict[SSID]['APs'] = list(set(file_dict[SSID]['APs']))
        else:
            file_dict[SSID] = {
                "APs": connected_APs,
                "Probes": probes
            }
    return file_dict

def main():
    basepath = aya.getBasePath()
    Filepaths = [(basepath / dev) for dev in args.survey]
    aya.CheckFilepaths(Filepaths)

    for path in Filepaths:
        GetAPs(path)

    for client in Clients:
        if len(Clients[client]['Probes']) > 1:
            print(client+":")
            print(Clients[client]['Probes'])

if __name__ == "__main__":
    main()