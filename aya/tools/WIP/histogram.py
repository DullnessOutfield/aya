import sqlite3
import glob
import datetime

histogram = [0]*24
db_glob = f'/placeholder/directory'
files = glob.glob(db_glob)
for file in files:
    conn = sqlite3.connect(file)
    cursor = conn.cursor()
    rows = cursor.execute('SELECT * from packets')
    try:
        for row in rows:
            timestamp = int(row[0])
            dt = datetime.datetime.fromtimestamp(timestamp)
            dt = dt.replace(minute=0, second=0)
            hr = (dt.hour - 4) % 24
            print(hr)
            histogram[hr] += 1
    except:
        pass
    conn.close()
total = sum(histogram)
percent = [int((i/total)*100) for i in histogram]
print(percent)