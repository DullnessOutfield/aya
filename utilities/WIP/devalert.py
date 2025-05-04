import time
import json
import requests

kismet_ip = '127.0.0.1'
kismet_user = 'username'
kismet_pass = 'password'
kismet_url = f'http://{kismet_user}:{kismet_pass}@{kismet_ip}:2501'
kismet_device_url = kismet_url+'/devices/by-key/{DEVICEKEY}/device.json'

kismet_recent_devices = kismet_url+'/devices/last-time/{TIMESTAMP}/devices.json'
devfile = './all-dev.txt'
soifile = './all-soi.txt'

def get_devs(filename):
    with open(filename) as f:
        devs = set(f.readlines())
    return devs

target = get_devs(devfile)
targetmac = [i.split(' ')[0][:-1] for i in target]
soi = get_devs(soifile)
# for i in targetmac:
#     for j in target:
#         if i in j:
#             print(j)

def cmd_devs(args):
    if len(args) == 0:
        ts = f'{(time.time() - 30):.5f}'
    elif args[0] == 'all':
        ts = 0
    else: 
        ts = f'{(time.time() - float(args[0])):.5f}'
    devs = activeDevices(ts)
    return devs

def activeDevices(fromTime):
    res = json.loads(requests.get(kismet_recent_devices.format(TIMESTAMP = fromTime)).text)
    macs = [i['kismet.device.base.macaddr'] for i in res]
    return macs

while True:
    soialert = []
    alert = []
    active = activeDevices(0)
    alert = list(set(active).intersection(targetmac))
    soialert = list(set(active).intersection(soi))
    if alert:
        for i in alert:
            for j in target:
                if i in j:
                    print(j)
        print('')
    if soialert:
        for i in soialert:
            print(f'#{i}')
        print('')
    if not soialert and not alert:
        print('...')
        time.sleep(2)