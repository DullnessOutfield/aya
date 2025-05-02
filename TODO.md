# TODO
## Library Modifications
### Classes
#### Class inheritence
- Would help with AltID and Airodump classes.
#### AirodumpDevice class
- Actually maybe a more generic "WirelessDevice" class which is gradually inhereted (e.g. WirelessDevice->WiFiDevice->KismetWiFiDevice->KismetAccessPoint)
#### HashCrackerDevice class
- Something that represents a device that breaks PMKID hashes. It should probably have an endpoint (REST? RabbitMQ?), a queue length, and a way for the client to retrieve their cracked password securely.
### Alternate Identifiers
### Alternate Identifier function
- Finds other devices which have been in geospatial proximity to it multiple times, allowing for coupling of identifiers together. This is good for showing clients tactics used by criminal/nefarious elements for findings CEOs etc.
### Alt Identifier attribute/dictionary
- Alt IDs aren't very useful unless you can then pull/filter/develop the associated identifiers

## Utility Porting
- Contact me for unported utilities if you want to help with the porting process.