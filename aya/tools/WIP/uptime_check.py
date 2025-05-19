from pathlib import Path
import aya

test_file = Path('/home/sigsec/Data/18MaySurvey/Kismet-20250518-20-47-34-1.kismet')
APs = aya.get_access_points(test_file)
for AP in APs:
    uptime = AP.dot11["dot11.device.bss_timestamp"]
    if uptime:
        print(uptime)