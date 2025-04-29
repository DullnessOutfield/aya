import argparse
import aya
from pathlib import Path
from aya import KismetDevice


parser = argparse.ArgumentParser()
parser.add_argument("survey", nargs="+", default=["test"])
args = parser.parse_args()

basepath = aya.getBasePath()


def ProcessProject(project_folder: Path):
    """
    Generates a dict of APs for a given project.
    Args:
        project_folder (Path): The folder for a given project, containing all the kismet files for that project

    Returns:
        dict: Contains all APs with SSID, Clients, and MAC
    """
    project_dict = {}
    files = project_folder.glob("**/*.kismet")
    for file in files:
        location: Path = Path(file).parent.name
        file_APs: list[KismetDevice] = aya.getAPs(file)
        file_dict = {}
        if file_APs:
            file_dict = ProcessFile(file_APs)
        for device in file_dict:
            file_dict[device]["Surveys"] = [location]
        project_dict = IntegrateFile(file_dict, project_dict)
    return project_dict


def IntegrateFile(new_file, master_file) -> dict:
    """
    Merges APs from a kismetdb file into an existing AP dict
    Args:
        new_file: AP dict of the kismetdb file
        master_file: AP dict of all previously processed kismetdb files

    Returns:
        dict: The master_file with new_file integrated
    """
    for device in new_file:
        if device not in master_file.keys():
            master_file[device] = new_file[device]
        else:
            for key in new_file[device]:
                master_file[device][key] += new_file[device][key]
                master_file[device][key] = list(set(master_file[device][key]))
    return master_file


def ProcessFile(kismet_devices: list[KismetDevice]) -> dict:
    """
    Generates a dict of APs for a given file.
    Args:
        kismet_devices (list[dict]): a list of kismetdb device dumps

    Returns:
        dict: Contains all APs with SSID, Clients, and MAC
    """
    file_dict = {}
    for device in kismet_devices:
        mac = device.mac
        SSID = device.json["kismet.device.base.commonname"]
        file_dict[SSID] = {"Clients": [], "Surveys": [], "MACs": []}
        Clients = device.getAPclients()
        if Clients:
            file_dict[SSID]["Clients"] = Clients
            file_dict[SSID]["MACs"] = [mac]
    return file_dict


def main():
    APs = {}
    projects: list[Path] = [basepath / project for project in args.survey]
    aya.CheckFilepaths(projects)
    for project in projects:
        project_APs: dict = ProcessProject(project)
        APs = IntegrateFile(project_APs, APs)
    for i in sorted(APs):
        print(i, APs[i])


if __name__ == "__main__":
    main()
