import itertools
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

channel_map = {}
for i in range(200):
    freq = (i*5)+5000
    for channelwidth in channelwidths:
        if i in channelwidth[0]:
            freqwidth = int(channelwidth[1]*.5)
    channel_map[i] = {"center":freq, "range":[freq-freqwidth,freq+freqwidth]}
    #print(i,freq)
for i in channel_map:
    print(i, channel_map[i])
