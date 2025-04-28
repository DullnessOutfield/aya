import glob
import os
import argparse
import csv
import aya

parser = argparse.ArgumentParser()
parser.add_argument("survey", nargs='+', default="")
args = parser.parse_args()

Clients = {}

def GetAPs(Folder):
    for i in glob.glob(Folder+'/**/*.kismet', recursive=True):
        devs = aya.getDevs(i)
        for j in devs:
            SSID = i["kismet.device.base.commonname"]
            if SSID not in Clients:
                Clients[SSID] = {"APs": [], "Probes": []}
                if 'dot11.device.associated_client_map' in i["dot11.device"].keys():
                    for AP in i["dot11.device"]['dot11.device.associated_client_map']:
                        if AP not in Clients[SSID]['APs']:
                            Clients[SSID]['APs'].append(AP)
                if 'dot11.device.probed_ssid_map' in i["dot11.device"].keys():
                    for probe in i["dot11.device"]["dot11.device.probed_ssid_map"]:
                        if len(probe["dot11.probedssid.ssid"]) > 0:
                            if probe not in Clients[SSID]['Probes']:
                                Clients[SSID]['Probes'].append(probe['dot11.probedssid.ssid'])
                                    
    for airo in glob.glob(Folder+'/**/Kismet/**/*.csv', recursive=True):
        with open(airo) as csvfile:
            sheet = csv.reader(csvfile)
            for i in sheet:
                if len(i):
                    SSID = i[0]
                    Probes = i[13:]
                    if SSID not in Clients:
                        Clients[SSID] = {"APs": [], "Probes": []}
                    for probe in Probes:
                        if probe not in Clients[SSID]['Probes'] and probe != ' ':
                            Clients[SSID]['Probes'].append(probe)

def main():
    basepath = aya.getBasePath
    Filepaths = [(i,basepath+i+'/') for i in args.survey]
    aya.CheckFilepaths(Filepaths)

    for path in Filepaths:
        GetAPs(path[1])

    for client in Clients:
        if len(Clients[client]['Probes']) > 1:
            print(client+":")
            print(Clients[client]['Probes'])

if __name__ == "__main__":
    main()