import argparse
from pathlib import Path
import aya

parser = argparse.ArgumentParser()
parser.add_argument("survey", nargs='+')
args = parser.parse_args()

basepath = aya.getBasePath()

def FindDevices(Folder: Path, soi_file: Path):
    for file in Folder.glob('**/*.kismet'):
        devices: list[aya.KismetDevice] = aya.find_soi(file, soi_file)
        for i in devices:
            print(i.mac, file)


def main():
    soi = Path('/home/sigsec/soi.txt')
    projects: list[Path] = [basepath / project for project in args.survey]
    aya.CheckFilepaths(projects)
    for project in projects:
        FindDevices(project, soi)

if __name__ == '__main__':
    main()