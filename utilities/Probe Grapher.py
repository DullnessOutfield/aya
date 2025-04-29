import kismetdb, json, os
from pathlib import Path
from glob import glob
import networkx as nx
import argparse
import pandas as pd
import aya
from aya import KismetDevice

DESIRED_TYPES = ['Wi-Fi Device', 'Wi-Fi Client', 'Wi-Fi Bridged']
BASEPATH = './Data/'

parser = argparse.ArgumentParser()
parser.add_argument("surveys", nargs='+', default="folder1")
args = parser.parse_args()

All_SSIDs = []
dictionary = {}

def ProcessProject(project: Path):
    for kismet_file in project.glob('**/*.kismet'):
        devices = aya.getSTAs(kismet_file)


def ProjectSummary(project_name, directory):
    project_dictionary = {}
    for i in glob(directory+'/**/*.kismet', recursive=True):
        print('Checking Probes in',i)
        try:
            devices = kismetdb.Devices(i).get_all()
        except:
            devices = FallbackDecode(i)
        for idx,device in enumerate(devices):
            if device['type'] in DESIRED_TYPES:
                MAC = device['devmac']
                if MAC not in project_dictionary:
                    node = GetNodeData(device)
                    project_dictionary[MAC] = node
                else:
                    SSID_List = device.GetProbes()
                    project_dictionary[MAC]['SSID'] += SSID_List

    project_dictionary = {i:project_dictionary[i]\
                        for i in project_dictionary\
                        if len(project_dictionary[i]['SSID']) > 0}
    project_hashdict = {hash(frozenset(project_dictionary[i]['SSID']+[project_name])):
                        {'MSN': project_name,
                         'MAC': project_dictionary[i]['MAC'],
                         'NAME': project_dictionary[i]['NAME'],
                        'SSID': project_dictionary[i]['SSID'],
                         'TYPE': 'DEVICE'}
                        for i in project_dictionary}
    return project_hashdict

def GetNodeData(devin):
    MACadd = devin['devmac']
    device_data = json.loads(devin['device'])
    name = device_data["kismet.device.base.commonname"]
    OUI = getOUI(MACadd)
    dot11 = device_data['dot11.device']
    SSID_List = GetProbes(devin)
    devnode = {'ID': len(dictionary),
                       'NAME': name,
                       'OUI': OUI,
                       'MAC': MACadd,
                       'SSID': SSID_List}
    return devnode
                    
def GenerateGraph(device_dictionary, SSID_dictionary):    
    nodes = [device_dictionary[i] for i in device_dictionary]
    SSID_list = [{'NAME': i, 'TYPE':'SSID', 'TimesSeen': 0, 'SeenAt': []} for i in SSID_dictionary]
    nodes += SSID_list
    G = nx.DiGraph()
    G.add_nodes_from(enumerate(nodes))
    for idx,node in enumerate(nodes):
        if 'SSID' in node.keys():
            for ssid in node['SSID']:
                SSID_ID = (SSID_dictionary.index(ssid))+len(device_dictionary)
                Loc_List = G.nodes()[SSID_ID]['SeenAt']
                if not(node['MSN'] in Loc_List):
                    G.nodes()[SSID_ID]['SeenAt'].append(node['MSN'])
                    G.nodes()[SSID_ID]['TimesSeen'] += 1
                G.add_edge(idx, SSID_ID)
    print(len(G.nodes()))
    nx.write_gml(G,'test.gml')

def main():
    nodes = {}
    projects: list[Path] = [basepath / project for project in args.project]
    aya.CheckFilepaths(projects)
    for project in projects:
        nodes = ProcessProject(project)
    GenerateGraph(dictionary, All_SSIDs)
    

if __name__ == '__main__':
    main()
