# Changelog
Under development !!

## [Unreleased]
- Support for Wattio Thermic
- Global cache for all components??
- Code cleanup and optimization

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
