import argparse
import aya
from aya import KismetDevice, WigleDevice
from pathlib import Path
parser = argparse.ArgumentParser()
parser.add_argument("projects", nargs='+')
args = parser.parse_args()
basepath = aya.get_basepath()

def append_to_mac_dict(project: str, macs: list[str], mac_dict):
    for mac in macs:
        if mac not in mac_dict:
            mac_dict[mac] = [project]
        elif project not in mac_dict[mac]:
            mac_dict[mac].append(project)
    return mac_dict

def parse_project(path: Path) -> list[str]:
    project_devices = set()
    for kismet in path.glob('**/*.kismet'):
        kismet_devices: list[KismetDevice] = aya.get_devs(kismet)
        macs: list[str] = [i.mac for i in kismet_devices]
        project_devices.update(macs)
    for wigle in path.glob('**/*.csv'):
        wigle_devices: list[WigleDevice] = aya.wigle.devices_from_csv(wigle)
        macs: list[str] = [i.mac for i in wigle_devices]
        project_devices.update(macs)
    return list(project_devices)

def main():
    projects: list[Path] = [basepath / project for project in args.projects]
    aya.check_filepaths(projects)
    mac_dictionary = {}
    for project in projects:
        MACList = parse_project(project)
        project_name = project.name
        mac_dictionary = append_to_mac_dict(project_name, MACList, mac_dictionary)
    common_devices = [i for i in mac_dictionary if len(mac_dictionary[i]) > 1]
    
    for device in common_devices:
        sightings = mac_dictionary[device]
        sighting_commas = ', '.join(sightings[:-1])
        sighting_and = sightings[-1]
        sighting_formatted = f"\t\tseen at {sighting_commas} and {sighting_and}"
        print(device, sighting_formatted)

if __name__ == "__main__":
    main()
