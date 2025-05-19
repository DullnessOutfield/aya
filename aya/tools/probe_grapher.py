from pathlib import Path
import networkx as nx
import argparse
import aya
from aya import KismetDevice

parser = argparse.ArgumentParser()
parser.add_argument("projects", nargs="+", default="folder1")
args = parser.parse_args()


def ProcessProject(project: Path):
    """
    Iterate through project to grab all probe requests made by all devices
    """
    project_dictionary = {}
    for kismet_file in project.glob("**/*.kismet"):
        devices = aya.get_stas(kismet_file)
        for device in devices:
            if device.mac not in project_dictionary:
                project_dictionary[device.mac] = device.probedSSIDs
            else:
                project_dictionary[device.mac] += device.probedSSIDs
    project_dictionary = {
        i: project_dictionary[i]
        for i in project_dictionary
        if len(project_dictionary[i]) > 0
    }
    return project_dictionary


def GetNodeData(dev: KismetDevice):
    devnode = {"NAME": dev.name, "MAC": dev.mac, "SSID": dev.probedSSIDs}
    return devnode


def isProbeSubset(mac1, mac2):
    return set(mac1).issubset(set(mac2))


def PruneDict(file_dictionary):
    """Remove keys whose value list is a subset of another's in the same dict."""
    keys = list(file_dictionary.keys())
    sets = {k: set(v) for k, v in file_dictionary.items()}
    to_remove = set()

    keys.sort(key=lambda k: len(sets[k]))

    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):  
            if sets[keys[i]].issubset(sets[keys[j]]):
                to_remove.add(keys[i])
 
    return {k: v for k, v in file_dictionary.items() if k not in to_remove}


def GenerateGraph(overall_dict):
    """
    Generate a gml graph based on probe requests, writes to basepath as 'graph.gml'
    Args:
        overall_dict (dict): Refer to main() and ProcessProject()
    """
    output = Path(aya.get_basepath() / "graph.gml")
    Graph = nx.Graph()
    ssid_nodes = set()
    for project_name, project_dict in overall_dict.items():
        project_dict = PruneDict(project_dict)
        for mac, node in project_dict.items():
            Graph.add_node(mac, label=mac, type="mac", project=project_name)

            for ssid in node:
                if ssid not in ssid_nodes:
                    Graph.add_node(ssid, label=ssid, type="ssid")
                    ssid_nodes.add(ssid)
                Graph.add_edge(mac, ssid)
    nx.write_gml(Graph, output)


def main():
    basepath = aya.get_basepath()
    nodes = {}
    projects: list[Path] = [basepath / project for project in args.projects]
    aya.check_filepaths(projects)
    for project in projects:
        nodes[project.name] = ProcessProject(project)
    GenerateGraph(nodes)


if __name__ == "__main__":
    main()
