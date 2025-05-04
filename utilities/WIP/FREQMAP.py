import sqlite3
import json
import glob
import itertools
import matplotlib.pyplot as plt

def Generate5GChannels():
    channelwidths=[[[180, 182, 184, 187, 189],10],\
                   [[34, 38, 46, 54, 62, 102, 110, 118, 126, 134, 142, 151, 159, 167, 175],40],\
                   [[42, 58, 106, 122, 138, 155, 171],80],\
                   [[50, 114, 163],160]]

    channelwidths.append([[i for i in range(200)\
                          if i not in\
                          list(itertools.chain(channelwidths[0][0]\
                                               ,channelwidths[1][0]\
                                               ,channelwidths[2][0]\
                                               ,channelwidths[3][0]))],20])
    for i in channelwidths:
        print(i)
    

    channel_map = {}
    for i in range(200):
        freq = (i*5)+5000
        for channelwidth in channelwidths:
            if i in channelwidth[0]:
                freqwidth = int(channelwidth[1]*.5)
        channel_map[i] = {"center":freq, "range":[freq-freqwidth,freq+freqwidth]}
        #print(i,freq)
    return channel_map

def Generate24GChannels():
    channel_map = {}
    for i in range(1,14):
        freq = 2407+(i*5)
        freqwidth = 11
        channel_map[i] = {"center":freq, "range":[freq-freqwidth,freq+freqwidth]}
    return channel_map


freqcount = {}
for kismet in glob.glob('./*.kismet', recursive=True):
    con = sqlite3.connect(kismet)
    cur = con.cursor()
    for j in cur.execute('select frequency, count(frequency) from packets where frequency > 0 group by frequency'):
        j = list(j)
        j[0] = int(j[0]*(10**-3))
        if j[0] not in freqcount:
            freqcount[j[0]] = j[1]
        else:
            freqcount[j[0]] += j[1]

print(freqcount)
channelmap5G = Generate5GChannels()
channelmap24G = Generate24GChannels()


for channel in channelmap5G:
    for i in freqcount:
        if channelmap5G[channel]['center'] == i:
            print(channel,freqcount[i])
    else:
        print(channel, 0)
            
for i,j in enumerate(freqcount):
    if j < 3000:
        for channel in channelmap24G:
            if channelmap24G[channel]['center'] == j:
                print(channel,freqcount[j])




minrange24 = 2400
maxrange24 = 2500
minrange50 = 5200
maxrange50 = 5900

channelmap24 = [[i,0] if i not in freqcount else [i,freqcount[i]] for i in range(minrange24,maxrange24)]
channelmap50 = [[i,0] if i not in freqcount else [i,freqcount[i]] for i in range(minrange50,maxrange50,20)]
