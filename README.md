# Aya
A collection of security auditing scripts for Kismet.

### Status
I have like 20 tools sitting in a folder on my desktop but they're all messy and some contain customer information, so I'm slowly making them presentable.

### Terminology
- Project - A folder containing kismetdb files belonging to one "job", however you define that. Could be one audit for one client, or one audit could have multiple projects for different sites. 
    - Basically, a lot of these scripts look to see if a device showed up on multiple projects, so if you want to see if devices showed up across multiple audits, structure it that way, if you want to see if they showed up at multiple buildings, structure it that way.
- Survey - An actual kismet file, currently focusing on Wi-Fi and Bluetooth datasources, rtl-sdr sources may be supported in the future once I get more familiar with them.

# Tools
APLister.py - Grabs all the Access Points from multiple projects and tells you the MAC, the SSID, which projects they showed up in, and the MAC addresses of all clients.