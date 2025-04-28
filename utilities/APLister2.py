import argparse
import os
import aya
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("survey", nargs="+", default=["test"])
args = parser.parse_args()

home = os.path.expanduser("~")
basepath = f"{home}/Data/"


def ProcessProject(project_folder: Path):
    project_dict = {}
    files = project_folder.glob('**/*.kismet')
    for file in files:
        location: Path = Path(file).parent.name
        kismet_file: list[dict] = aya.getAPs(file)
        file_dict = {}
        if kismet_file:
            file_dict = ProcessFile(kismet_file)
        for device in file_dict:
            file_dict[device]["Surveys"] = [location]
        project_dict = IntegrateFile(file_dict, project_dict)
    return project_dict


def IntegrateFile(new_file, master_file) -> dict:
    for device in new_file:
        if device not in master_file.keys():
            master_file[device] = new_file[device]
        else:
            for key in new_file[device]:
                master_file[device][key] += new_file[device][key]
                master_file[device][key] = list(set(master_file[device][key]))
    return master_file


def ProcessFile(kismet_devices) -> dict:
    file_dict = {}
    for device in kismet_devices:
        mac = device["kismet.device.base.macaddr"]
        SSID = device["kismet.device.base.commonname"]
        file_dict[SSID] = {"Clients": [], "Surveys": [], "MACs": []}
        Clients = aya.getAPclients(device)
        if Clients:
            file_dict[SSID]["Clients"] = Clients
            file_dict[SSID]["MACs"] = [mac]
    return file_dict

def main():
    APs = {}
    projects: list[Path] = [Path(basepath + project) for project in args.survey]
    aya.CheckFilepaths(projects)
    for project in projects:
        project_APs: dict = ProcessProject(project)
        APs = IntegrateFile(project_APs, APs)
    for i in sorted(APs):
        print(i, APs[i])


if __name__ == "__main__":
    main()
