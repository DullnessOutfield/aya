import csv


def find_soi(file, soi_file):
    with open(soi_file) as f:
        soi_list = f.readlines()
    soi_list = [i.lower().strip() for i in soi_list if i.strip()]
    devices = devices_from_csv(file)
    hits = [i for i in devices if i.identifier in soi_list]
    return hits

def devices_from_csv(file):
    from ..classes import WigleDevice
    with open(file) as f:
        raw_file = f.readlines()[2:]
    csvdata = csv.reader(raw_file)
    devices = [WigleDevice.from_record(i) for i in csvdata]
    return devices