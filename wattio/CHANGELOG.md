# Changelog
Under development !!

## [0.2.0]
### Added
- Support for Wattio Thermic. Need extra testing on winter time ;)
- Battery status for supported devices

### Changed
- Full Code changed to platform and async methods, only one API request for all devices
- Pod device changed from Light to Switch. Support for power consumption at entity
- Code cleanup and optimization

### IMPORTANT UPGRADE INFO 
No need to change wattio.conf or re-authorize the app, but **the way the platform is configured HAS CHANGED**.

New configuration.yaml example:

```yaml
wattio:
  scan_interval: 60 (OPTIONAL: time in seconds, defaults to 30)
  therm_max_temp: 30 (OPTIONAL: Max temp for climate component, defaults to 30)  
  therm_min_temp: 10 (OPTIONAL: Min temp for climate component, defaults to 10)
```

## [0.1.2] - 2019-06-05
### Added
- Support for Motion's presence sensor

### Changed
- Better code formatting and linting

## [0.1.1] - 2019-05-31
### Added
- Support for Wattio PODs
- POD state detection (Available / Not available)
- Support for Wattio Doors

### Changed
- Some interface messages changes. (First setup)
- Better debugging/error log messages.
- Some code moved to __init__.py for reutilization in multiple components.

### Fixed
- Some excepcion handling (work pending in progress ...)

## [0.1.0] - 2019-05-26
### Added
- Initial configuracion information from Hass Interface.
- Wattio Oauth2 API authorization throught Hass Interface.
- Sensor discovery and configuration for BATs, PODs (Power consumption), Thermics and Motion (Temp only).
- One API request query for all sensors
