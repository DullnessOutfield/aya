import argparse
from pathlib import Path
import aya

parser = argparse.ArgumentParser()
parser.add_argument("survey", nargs='+')
args = parser.parse_args()

basepath = aya.get_basepath()

def find_kismet_devices(Folder: Path, soi_file: Path):
    for file in Folder.glob('**/*.kismet'):
        with open(soi_file) as f:
            soi_list = f.readlines()
        soi_list = [f'{i.upper().strip()}' for i in soi_list if i.strip()]
        soi_devices = [aya.classes.WiFiDevice(i) for i in soi_list]
        devices = aya.find_soi(file, soi_devices)

        if devices:
            for i in devices:
                print(i.mac, file)

def find_wigle_devices(folder: Path, soi_file: Path):
    for file in folder.glob('**/*.csv'):
        devices: list[aya.WigleDevice] = aya.wigle.find_soi(file, soi_file)
        
        for device in devices:
            print(device.identifier, file)

def main():
    soi = Path('/home/sigsec/soi.txt')
    projects: list[Path] = [basepath / project for project in args.survey]
    aya.check_filepaths(projects)
    for project in projects:
        find_kismet_devices(project, soi)
        find_wigle_devices(project, soi)

if __name__ == '__main__':
    main()