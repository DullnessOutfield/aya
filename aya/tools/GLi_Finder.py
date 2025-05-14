import argparse
from pathlib import Path
import aya

parser = argparse.ArgumentParser()
parser.add_argument("survey", nargs='+')
args = parser.parse_args()

basepath = aya.getBasePath()

def FindDevices(Folder: Path):
    for i in Folder.glob('**/*.kismet'):
        devices: list[aya.KismetDevice] = aya.findOUIMatches(i, aya.oui.GLinet)
        for i in devices:
            print(i.mac)


def main():
    projects: list[Path] = [basepath / project for project in args.survey]
    aya.CheckFilepaths(projects)
    for project in projects:
        FindDevices(project)

if __name__ == '__main__':
    main()