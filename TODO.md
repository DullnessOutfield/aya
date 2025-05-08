# TODO
## Library Modifications
### Classes
#### Class inheritence
- Try migrating some of the KismetDevice methods up to parent classes where applicable
#### Bluetooth 
- Child of WirelessDevice
#### RF class (433/ADS-B)
- This is a longer-term idea. 433/adsb would be easy starts since they're already implemented in Kismet but more HAM radio type stuff would be interesting.
#### AirodumpDevice class
- A class that inherits WiFi Device and generates device objects from airodump files
#### HashCrackerDevice class
- Something that represents a device that breaks PMKID hashes. It should probably have an endpoint (REST? RabbitMQ?), a queue length, and a way for the client to retrieve their cracked password securely.
### Alternate Identifiers
### Alternate Identifier function
- Finds other devices which have been in geospatial proximity to it multiple times, allowing for coupling of identifiers together. This is good for showing clients tactics used by criminal/nefarious elements for findings CEOs etc.
### Alt Identifier attribute/dictionary
- Alt IDs aren't very useful unless you can then pull/filter/develop the associated identifiers

### Design
#### Project/Survey
- Figure out a more elegant way to manage kismetdb files and associate them with jobs/locations/events/ how to generally organize them.

### Functions
- A tool that derives pseudo-KismetDevices based on probe hashes
- A tool that derives pseudo-probe hashes based on observing probes consistently occurring sequentially alongside consistently incrementing sequence numbers
    - Sub-ToDo: Find the research paper I stole this idea from to explain it better

## Tools 
### Porting
- Contact me for unported tools if you want to help with the porting process.
### New
- A tool that grabs every device seen between two files, and notes which file had a stronger rssi