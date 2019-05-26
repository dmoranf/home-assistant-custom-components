# Home-Assistant Custom Components
This information is also available in [Spanish](./README.es.md)


Components
------------
   * [fortigate device tracker](#Fortigate-Device-Tracker): Fortigate's Device detection through WEB-API.
   * [Wattio Smart Home](#Wattio-Smart-Home): Wattio Smart Home platform integration (Under development).
      
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

 - Tested on FortiOS 6.0.4 and Home Assistant 0.90.2
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
    timeout: 120
    
```

Vars:

- **host**: IP Address / Host name of Fortigate's management interface.
- **port** (*Optional*): HTTPs service port (443 by default).
- **username**: Username for API access.
- **password**: Password for API access.
- **consider_home**: (*Optional*) Timeout to set the device as "away" after the configured timeout.
- **interval_seconds**: (*Optional*) Time between discovery request to Fotigate's API.
- **timeout**: (*Optional*) Time to detect the device as offline, in seconds (Defaults to 60).

### Credits

 - [FortiOS Tracker](https://community.home-assistant.io/t/fortios-device-tracker/28333/4) from [Mister_Slowhand](https://community.home-assistant.io/u/Mister_Slowhand): FortiOS Device Tracker (ARP and SSH)


----------------------------

### Wattio Smart Home

Wattio Smart Home platform integration for Home Assistant throught Wattio's API. This component is under development, please check CHANGELOG.md for last updates..


### Requisites

 - Client ID and Secret for Wattio Platform (Request to wattio Support)
 - Tested on Home Assistant 0.90.2

### Installation

- Copy "wattio" folder to your `<config dir>/custom_components/wattio` directory.
- Configure as shown below.
- Restart HASS.
- Follow the adittional configuration steps.

### Configuration

Add the following to your `configuration.yaml`.

```yaml
# Wattio Sensors
sensor:
  - platform: wattio
    scan_interval: 300
```

Vars:
 - scan_interval: Time to refresh data and between requests to Wattio API.

### Adittional steps

 - At first launch a new notification is shown at the UI requesting the user to configure de user id and the secret
 - After changing the configuration file, another notification should appear asking the user to authorize home assistant at wattio.
 - Follow the link for authorization, a page requesting username and password from Wattio should be shown.
 - Finally, close the notification and refresh your GUI.

<p align="center">
<img src="https://raw.githubusercontent.com/dmoranf/home-assistant-custom-components/master/_screenshots/wattio_configuration.gif"></p>

  
