import glob
import os
import argparse
import csv
import aya
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("survey", nargs='+', default="")
args = parser.parse_args()

Clients = {}

def GetAPs(Folder: Path):
    parseKismetdb(Folder)
    parseAirodump(Folder)
                                        

def parseAirodump(Folder: Path):
     for airo in Folder.glob('**/Kismet/**/*.csv'):
        with open(airo) as csvfile:
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

def parseKismetdb(Folder: Path):
    for file in Folder.glob('**/*.kismet'):
        devs = aya.getSTAs(file)
        for dev in devs:
            SSID = dev["kismet.device.base.commonname"]
            if SSID not in Clients:
                Clients[SSID] = {"APs": [], "Probes": []}
                if 'dot11.device.associated_client_map' in dev["dot11.device"].keys():
                    for AP in dev["dot11.device"]['dot11.device.associated_client_map']:
                        if AP not in Clients[SSID]['APs']:
                            Clients[SSID]['APs'].append(AP)
                if 'dot11.device.probed_ssid_map' in dev["dot11.device"].keys():
                    for probe in dev["dot11.device"]["dot11.device.probed_ssid_map"]:
                        if len(probe["dot11.probedssid.ssid"]) > 0:
                            if probe not in Clients[SSID]['Probes']:
                                Clients[SSID]['Probes'].append(probe['dot11.probedssid.ssid'])


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