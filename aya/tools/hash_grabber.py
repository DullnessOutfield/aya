import argparse
from pathlib import Path
import aya

parser = argparse.ArgumentParser()
parser.add_argument("project", nargs="+")
args = parser.parse_args()

basepath = aya.get_basepath()


def process_project(project_folder: Path):
    project_hashes = {}
    for kismet_file in project_folder.glob("**/*.kismet"):
        APs = aya.get_access_points(kismet_file)
        for AP in APs:
            handshake = AP.hashes
            if handshake:
                project_hashes[AP.mac] = {"Hash": handshake, "SSID": AP.name}
    return project_hashes


def main():
    hashes = {}
    projects: list[Path] = [basepath / project for project in args.project]
    aya.check_filepaths(projects)
    for project in projects:
        hashes.update(process_project(project))
    for mac in sorted(hashes):
        print(mac, hashes[mac])


if __name__ == "__main__":
    main()
