import argparse, os, json, pathlib
import aya
# import kismetdb
from glob import glob


parser = argparse.ArgumentParser()
parser.add_argument("survey", nargs='+', default=["test"])
args = parser.parse_args()

home = os.path.expanduser("~")
basepath = f'{home}/Data/'

def ProcessProject(project_folder):
	project_dict = {}
	files = glob(project_folder+'/**/*.kismet', recursive=True)
	print(files)
	for file in files:
		location = pathlib.Path(file).parent.name
		kismet_file = aya.getAPs(file)
		file_dict = {}
		if kismet_file:
			file_dict = ProcessFile(kismet_file)
		for device in file_dict:
			file_dict[device]['Surveys'] = [location]
		project_dict = IntegrateFile(file_dict, project_dict)	
	return project_dict

def IntegrateFile(new_file, master_file):
	for device in new_file:
		if not(device in master_file.keys()):
			master_file[device] = new_file[device]
		else:
			for key in new_file[device]:
				master_file[device][key] += new_file[device][key]
				master_file[device][key] = list(set(master_file[device][key]))
	return master_file

def ProcessFile(kismet_devices):
    file_dict = {}
    SSIDs = []
    for device in kismet_devices:
        mac = device['kismet.device.base.macaddr']
        SSID = device['kismet.device.base.commonname']
        file_dict[SSID] = {'Clients':[], 'Surveys':[], 'MACs':[]}
        dot11 = device['dot11.device']
        if 'dot11.device.associated_client_map' in dot11.keys():
            Clients = [i for i in dot11['dot11.device.associated_client_map']]
            file_dict[SSID]['Clients'] = Clients
            file_dict[SSID]['MACs'] = [mac]
    return file_dict


def WriteResults(Project_APs):
	return 0

def IntegrateProject(All_APs, Project_APs):
	return 0	

def main():
	APs = {}
	projects = [basepath + project for project in args.survey]
	aya.CheckFilepaths(projects)
	for project in projects:
		project_APs = ProcessProject(project)
		WriteResults(project_APs)
		APs = IntegrateFile(project_APs, APs)
	for i in sorted(APs):
            print(i, APs[i]['MACs'])

if __name__ == '__main__':
	main()
