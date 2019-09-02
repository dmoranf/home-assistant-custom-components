# Home-Assistant Custom Components
This information is also available in [Spanish](./README.es.md)


Components
------------
   * [fortigate device tracker](#Fortigate-Device-Tracker): Fortigate's Device detection through WEB-API.
   * [Wattio Smart Home](#Wattio-Smart-Home): Wattio Smart Home platform integration (Under development).
      
----------------------------

## Fortigate Device Tracker
<img src="https://img.shields.io/badge/Version-0.1.3-green.svg" />

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

 - Tested on FortiOS 6.0.4 and Home Assistant >= 0.90.2 (Tested on 0.98.2)
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

| Var | Description |
| --- | --- |
| **host** | IP Address / Host name of Fortigate's management interface. |
| **port** | (*Optional*)  HTTPs service port (443 by default). |
| **username** | Username for API access. |
| **password** | Password for API access. |
| **consider_home** | (*Optional*) Timeout to set the device as "away" after the configured timeout. |
| **interval_seconds** | (*Optional*) Time between discovery request to Fotigate's API. |
| **timeout** | (*Optional*) Time to detect the device as offline, in seconds (Defaults to 60). |

### Credits

 - [FortiOS Tracker](https://community.home-assistant.io/t/fortios-device-tracker/28333/4) from [Mister_Slowhand](https://community.home-assistant.io/u/Mister_Slowhand): FortiOS Device Tracker (ARP and SSH)


----------------------------

### Wattio Smart Home
<img src="https://img.shields.io/badge/Version-0.2.1-green.svg" />

Wattio Smart Home platform integration for Home Assistant throught Wattio's API. This component is under development, please check [CHANGELOG.md](https://github.com/dmoranf/home-assistant-custom-components/blob/master/wattio/CHANGELOG.md) for last updates.

Link: [Wattio SmartHome](https://wattio.com/)

### Important Info

Since Hass 0.96, the way climate devices work has been changed and it is NOT backward compatible. Default (included) climate.py works for HASS versions >= 0.96, but a file called climate.py_pre_096 is available for use if you are using HASS between 0.92 and 0.96. Just make a backup of climate.py and rename climate.py_pre_096 to climate.py

### Screenshots

 - Wattio Sensors (Bat & Thermic examples):

<p align="center">
<img src="https://raw.githubusercontent.com/dmoranf/home-assistant-custom-components/master/_screenshots/wattio_bat_sensor.png" width="300px">   &nbsp;&nbsp;  <img src="https://raw.githubusercontent.com/dmoranf/home-assistant-custom-components/master/_screenshots/wattio_thermic_sensor.png" width="300px"></p>

- Wattio Binary Sensors (Door example):

<p align="center">
<img src="https://raw.githubusercontent.com/dmoranf/home-assistant-custom-components/master/_screenshots/wattio_door_sensor.png" width="300px"></p>

- Wattio Switch (Pod example):

<p align="center">
<img src="https://raw.githubusercontent.com/dmoranf/home-assistant-custom-components/master/_screenshots/wattio_pod_switch.png" width="300px"></p>

### Requisites

 - Client ID and Secret for Wattio Platform (Request to wattio Support)
 - Works on Home Assistant >= 0.90.2 (Tested on 0.98.2)

### Installation

- Copy "wattio" folder to your `<config dir>/custom_components/wattio` directory.
- Configure as shown below.
- Restart HASS.
- Follow the adittional configuration steps.

### Configuration

Add the following to your `configuration.yaml`.

> From version 0.2.0 the way of Wattio component is configured has been changed. If you are upgrading for a previous version you **MUST CHANGE YOUR CONFIG FILE**

```yaml
# Wattio Platform
wattio:
    scan_interval: 60
    therm_max_temp: 30
    therm_min_temp: 10 
```

Vars:

| Var | Description |
| --- | --- |
| *scan_interval* | OPTIONAL - Time (in seconds) between data updates , defaults to 30 seconds |
| *therm_max_temp* | OPTIONAL - Max configurable temp for thermic devices, defaults to 30 degrees |
| *therm_min_temp* | OPTIONAL - Min configurable temp for thermic devices, defaults to 10 degrees |

### Adittional steps

 - At first launch a new notification is shown at the UI requesting the user to configure de user id and the secret. 
 - The configuration file "wattio.conf" is created automatically.
 - Change user id and secret in "wattio-conf".

   > User id and secret MUST be supplied by wattio team (This is not your user and password!)

 - After changing the configuration file, another notification should appear asking the user to authorize home assistant at wattio.
 - Follow the link for authorization, a page requesting username and password from Wattio should be shown.
 - Finally, close the notification and refresh your GUI.
 - Once devices has been added to HASS, first data update will take place after the configured scan_interval.


<p align="center">
<img src="https://raw.githubusercontent.com/dmoranf/home-assistant-custom-components/master/_screenshots/wattio_config.gif"></p>

  
