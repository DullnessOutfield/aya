import argparse
from pathlib import Path
import aya

parser = argparse.ArgumentParser()
parser.add_argument("survey", nargs='+')
args = parser.parse_args()

basepath = aya.get_basepath()

def FindDevices(Folder: Path):
    for i in Folder.glob('**/*.kismet'):
        devices: list[aya.KismetDevice] = aya.find_oui_matches(i, aya.oui.Espressif)
        for i in devices:
            print(i.mac)


def main():
    projects: list[Path] = [basepath / project for project in args.survey]
    aya.check_filepaths(projects)
    for project in projects:
        FindDevices(project)

if __name__ == '__main__':
    main()