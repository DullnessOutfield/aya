# Aya
A collection of security auditing scripts for Kismet.

### Status
I have like 20 tools sitting in a folder on my desktop but they're all messy and some contain customer information, so I'm slowly making them presentable.

Feel free to help with:
- Documentation
- Tests
- A class for probe fingerprints
- Any device fingerprinting methods I haven't thought of
- A script that extracts car make/model from AndroidAP beacons
- A script that compares RSSI values of APs between surveys/projects (Would help in cases where you're trying to figure out if an AP is inside our outside a given office/server room)
- A GUI/TUI/CLI frontend/any amount of UX whatsoever please help
- Really help however tbh idk

### Terminology
- Project - A folder containing kismetdb files belonging to one "job", however you define that. Could be one audit for one client, or one audit could have multiple projects for different sites. 
    - Basically, a lot of these scripts look to see if a device showed up on multiple projects, so if you want to see if devices showed up across multiple audits, structure it that way, if you want to see if they showed up at multiple buildings, structure it that way.
- Survey - An actual kismet file, currently focusing on Wi-Fi and Bluetooth datasources, rtl-sdr sources may be supported in the future once I get more familiar with them.
- AP - Wi-Fi Access Point
- STA - Wi-Fi device (anything not AP or Ad-Hoc)

# Tools
APLister.py - Grabs all the Access Points from multiple projects and tells you the MAC, the SSID, which projects they showed up in, and the MAC addresses of all clients.

APNTR.py - Shows any STA probing for multiple APs.

WITWIJO.py - Where in the World is Johnny's iPhone? (finger slipped). Looks for devices common across multiple projects. 

##### License
The only rule is every day you launch this software I'm allowed to make you think of a number between 1 and 1000 and if I get it right you have to give me $5.
