import argparse
import aya
from aya import KismetDevice
from pathlib import Path
parser = argparse.ArgumentParser()
parser.add_argument("projects", nargs='+')
args = parser.parse_args()
basepath = aya.getBasePath()

def AppendToMACDict(project: str, MACs: list[str], MACDict):
    for mac in MACs:
        if mac not in MACDict:
            MACDict[mac] = [project]
        elif project not in MACDict[mac]:
            MACDict[mac].append(project)
    return MACDict

def parse_project(path: Path) -> list[str]:
    project_devices = set()
    for kismet in path.glob('**/*.kismet'):
        devices: list[KismetDevice] = aya.getDevs(kismet, 'all')
        devices: list[str] = [i.mac for i in devices]
        project_devices.update(devices)
    return list(project_devices)

def main():
    projects: list[Path] = [basepath / project for project in args.projects]
    aya.CheckFilepaths(projects)
    MACDictionary = {}
    for project in projects:
        MACList = parse_project(project)
        project_name = project.name
        MACDictionary = AppendToMACDict(project_name, MACList, MACDictionary)
    CommonDevices = [i for i in MACDictionary if len(MACDictionary[i]) > 1]
    
    for Device in CommonDevices:
        Sightings = MACDictionary[Device]
        Sighting_Commas = Sightings[:-1]
        Sighting_And = Sightings[-1]
        Sighting_Formatted = "\t\tseen at {0} and {1}".format(', '.join(Sighting_Commas), Sighting_And)
        print(Device, Sighting_Formatted)

if __name__ == "__main__":
    main()
