import kismetdb, json
from glob import glob
basepath = '/home/user/Desktop/Data/Client1_2022'


def main():
    ssid_dict = {}
    for phase in glob(basepath+'/*/'):
        phase_name = phase.split('\\')[-2]
        for file in glob('{}/*.kismet'.format(phase)):
            devices = kismetdb.Devices(file).get_all()
            for device in devices:
                if device['type'] in ['Wi-Fi Device','Wi-Fi Client']:
                    devjson = json.loads(device['device'])
                    dot11 = devjson['dot11.device']
                    if 'dot11.device.probed_ssid_map' in dot11.keys():
                        probemap = dot11['dot11.device.probed_ssid_map']
                        for probe in probemap:
                            if probe['dot11.probedssid.ssid']:
                                ssid = probe['dot11.probedssid.ssid']
                                if ssid not in ssid_dict:
                                    ssid_dict[ssid] = [phase_name]
                                else:
                                    ssid_dict[ssid].append(phase_name)
    for i in ssid_dict:
        ssid_dict[i] = set(sorted(ssid_dict[i]))
        print(i)
        print('\t',ssid_dict[i])


main()
