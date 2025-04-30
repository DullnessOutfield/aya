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
    project_dictionary = {}
    for kismet_file in project.glob('**/*.kismet'):
        devices = aya.getSTAs(kismet_file)
        for device in devices:
            if device.mac not in project_dictionary:
                node = GetNodeData(device)
                project_dictionary[device.mac] = node
            else:
                project_dictionary[device.mac]['SSID'] += device.probedSSIDs
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

def GetNodeData(dev: KismetDevice):
    devnode = {'ID': len(dictionary),
                       'NAME': dev.name,
                       'MAC': dev.mac,
                       'SSID': dev.probedSSIDs}
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
    basepath = aya.getBasePath()
    nodes = {}
    projects: list[Path] = [basepath / project for project in args.project]
    aya.CheckFilepaths(projects)
    for project in projects:
        nodes = ProcessProject(project)
    GenerateGraph(dictionary, All_SSIDs)
    

if __name__ == '__main__':
    main()
