import sqlite3, glob, json, os, argparse, csv

class KismetdbExtractError(Exception):
    pass

'''
Take a row from the kismetdb device table and return the json data as a dict
'''
def extract_json(row: tuple) -> dict:
    rawjson = str(row).split(',',14)[-1]
    try:
        real_json = json.loads(rawjson[3:-2])
    except json.decoder.JSONDecodeError as e: 
        raise KismetdbExtractError(f'Failed to parse device; {e}')
    return real_json

'''
Get all Access Points from a kismet file
'''
def getAPs(kismet_file: str) -> list[dict]:
    con = sqlite3.connect(kismet_file)
    cur = con.cursor()
    cur.execute("select * from devices where type == 'Wi-Fi AP'")
    APs = []
    for AP in cur:
        APs.append(extract_json(AP))
    return APs

def CheckFilepaths(Filepaths):
    for path in Filepaths:
        if not os.path.exists(path):
            raise FileNotFoundError(f'{path} does not exist.') 
    return 0

# x = getAPs('/home/sigsec/Data/Kismet-20250428-15-58-49-1.kismet')
# y = extract_json((1,2))