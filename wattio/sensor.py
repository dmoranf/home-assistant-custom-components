"""Platform for Wattio integration testing."""
import logging

from homeassistant.const import (ATTR_BATTERY_LEVEL, STATE_OK,
                                 STATE_UNAVAILABLE, TEMP_CELSIUS)
from homeassistant.helpers.entity import Entity

from . import DOMAIN, WattioDevice

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Wattio Sensor setup platform."""
    _LOGGER.debug("Wattio Sensor component running ...")
    if discovery_info is None:
        _LOGGER.error("No Sensor(s) discovered")
        return
    devices = []
    for device in hass.data[DOMAIN]["devices"]:
        measurement = None
        icon = None
        if device["type"] == "pod":
            icon = "mdi:power-socket-eu"
            measurement = "Watt"
            devices.append(WattioSensor(device["name"],
                                        device["type"],
                                        measurement,
                                        icon,
                                        device["ieee"]
                                        ))
            _LOGGER.debug("Adding device: %s", device["name"])
        if device["type"] == "bat":
            measurement = "Watt"
            devices.append(WattioSensor(device["name"],
                                        device["type"],
                                        measurement,
                                        icon,
                                        device["ieee"],
                                        device["channel"]
                                        ))
            _LOGGER.debug("Adding device: %s", device["name"])
        if device["type"] == "therm":
            measurement = TEMP_CELSIUS
            devices.append(WattioSensor(device["name"],
                                        device["type"],
                                        measurement,
                                        icon,
                                        device["ieee"]
                                        ))
            _LOGGER.debug("Adding device: %s", device["name"])
        if device["type"] == "motion":
            measurement = TEMP_CELSIUS
            devices.append(WattioSensor(device["name"],
                                        device["type"],
                                        measurement,
                                        icon,
                                        device["ieee"]
                                        ))
            _LOGGER.debug("Adding device: %s", device["name"])
    async_add_entities(devices)


class WattioSensor(WattioDevice, Entity):
    """Representation of Sensor."""

    def __init__(self, name, devtype, measurement, icon, ieee, channel=None):
        """Initialize the sensor."""
        self._pre = "s_"
        self._name = name
        self._state = None
        self._measurement = measurement
        self._icon = icon
        self._ieee = ieee
        self._devtype = devtype
        self._channel = None
        self._battery = None
        self._data = None
        if channel is not None:
            self._channel = channel-1

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def available(self):
        """Return availability."""
        if self._data is not None:
            status = 0
            for device in self._data:
                if self._channel is not None and device["ieee"] == self._ieee:
                    status = 1
                    break
                elif device["ieee"] == self._ieee:
                    status = 1
                    break
            if status == 1:
                _LOGGER.debug("Device %s - available", self._name)
                return STATE_OK
            else:
                _LOGGER.debug("Device %s - NOT available", self._name)
                return STATE_UNAVAILABLE

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._measurement

    @property
    def icon(self):
        """Return the image of the sensor."""
        return self._icon

    @property
    def state(self):
        """Return sensor state."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes of this device."""
        attr = {}
        if self._battery is not None:
            attr[ATTR_BATTERY_LEVEL] = self.get_battery_level()
        return attr

    def get_battery_level(self):
        """Return device battery level."""
        if self._battery is not None:
            battery_level = round((self._battery*100)/4)
            return battery_level

    async def async_update(self):
        """Update sensor data."""
        self._data = self.hass.data[DOMAIN]["data"]
        _LOGGER.error("ACTUALIZANDO SENSOR %s - %s", self._name, self._ieee)
        if self._data is not None:
            for device in self._data:
                if device["ieee"] == self._ieee:
                    if self._channel is not None and self._devtype == "bat":
                        sensorvalue = device["status"]["consumption"][self._channel]
                    elif self._devtype == "therm":
                        sensorvalue = device["status"]["current"]
                    elif self._devtype == "motion":
                        sensorvalue = device["status"]["temperature"]
                        self._battery = device["status"]["battery"]
                    elif self._devtype == "pod":
                        sensorvalue = device["status"]["consumption"]
                    else:
                        sensorvalue = None
                    self._state = sensorvalue
                    break
            _LOGGER.debug("Valor: %s", self._state)
            return self._state
        else:
            return False

        '''
        if sensordata == 0:
            return None
        if self._channel is not None and self._devtype == "bat":
            sensorvalue = sensordata["consumption"][self._channel]
        elif self._devtype == "therm":
            sensorvalue = sensordata["current"]
        elif self._devtype == "motion":
            sensorvalue = sensordata["temperature"]
            self._battery = sensordata["battery"]
        elif self._devtype == "pod":
            sensorvalue = sensordata["consumption"]
        else:
            sensorvalue = sensordata
        '''
        _LOGGER.debug("Updating sensor %s: %s", self._name, sensorvalue)
        self._state = 0
