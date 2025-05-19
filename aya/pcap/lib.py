import pyshark

def get_devs(filename):
    capture = pyshark.FileCapture(filename)

    print(capture[5])

get_devs('/home/sigsec/courtyardusm.pcap')