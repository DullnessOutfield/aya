import sqlite3, glob, json, os
def GetProbes(Folder):
    Probe_List = []
    for i in glob.glob(Folder+'/**/*.kismet', recursive=True):
        print(i)
        con = sqlite3.connect(i)
        cur = con.cursor()
        cur.execute("select * from devices where type = 'BTLE Device'")
        names = list(map(lambda x: x[0], cur.description))
        for j in cur:
            rawjson = str(j).split(',',14)[-1]
            real_json = json.loads(rawjson[3:-2])
            common_name=real_json["kismet.device.base.commonname"]
            if ":" not in common_name:
                print(j[4],real_json["kismet.device.base.commonname"])
    return Probe_List

A_Probes = GetProbes('../../A')

