# Home-Assistant Custom Components
This information is also available in [Spanish](./README.es.md)


Components
------------
   * [fortigate device tracker](#Fortigate-Device-Tracker): Fortigate's Device detection through WEB-API.
      
----------------------------

## Fortigate Device Tracker

If enabled, Fortigate unit tracks the status and gathers different information about the devices connected to your network. This component grabs this information via Fortigate's API requests.

Device inventory is available at  `User & Device -> Device inventory`:


<p align="center">
<img src="https://raw.githubusercontent.com/dmoranf/home-assistant-custom-components/master/_screenshots/fortigate_device_detection.png" width="600px"></p>


Firewall shows if devices are online or offline based on a configured timeout. This timeout defaults to 5 minutes, but it could be changed through CLI:

```
config system global
set device-idle-timeout 300
end
```

Fortigate's API returns a LAST_SEEN value instead of the device status (Online or Offline), so timeout values configured at HASS level are applied. If you want the information to be consistent across systems, it's recommended to set *device-idle-timeout* and *consider_home* parameters with same values.


### Requisites

 - Tested on FortiOS 6.0.4
 - Device discovery enabled on the Fortigate at interface level

### Installation

- Copy "fortigate_tracker" folder to your `<config dir>/custom_components/fortigate_tracker` directory.
- Configure as shown below.
- Restart HASS.

### Configuration

Add the following to your `configuration.yaml`.

```yaml
# Fortigate DeviceTracker
device_tracker:
  - platform: fortigate
    host: HOST
    port: HTTPS_PORT
    username: !secret FG_USERNAME
    password: !secret FG_PASSWORD
    consider_home: 300
    interval_seconds: 120
    
```

Vars:

- **host**: IP Address / Host name of Fortigate's management interface.
- **port** (*Optional*): HTTPs service port (443 by default).
- **username**: Username for API access.
- **password**: Password for API access.
- **consider_home**: (*Optional*) Timeout before considering the device out of home.
- **interval_seconds**: (*Optional*) Time between discovery request to Fotigate's API.

### Credits

 - [FortiOS Tracker](https://community.home-assistant.io/t/fortios-device-tracker/28333/4) from [Mister_Slowhand](https://community.home-assistant.io/u/Mister_Slowhand): FortiOS Device Tracker (ARP and SSH)


----------------------------


