"""Platform for Wattio integration testing."""
import logging

from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.const import ATTR_BATTERY_LEVEL, STATE_OK, STATE_UNAVAILABLE

from . import DOMAIN, WattioDevice


_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Configure Wattio Binary Sensor."""
    _LOGGER.debug("Wattio Binary Sensor component running ...")
    if discovery_info is None:
        _LOGGER.error("No Binary Sensor device(s) discovered")
        return
    devices = []
    for device in hass.data[DOMAIN]["devices"]:
        icon = None
        if device["type"] == "door":
            icon = "mdi:door"
            devices.append(WattioBinarySensor(device["name"],
                                              device["type"],
                                              icon,
                                              device["ieee"]
                                              ))
            _LOGGER.debug("Adding device: %s", device["name"])
        if device["type"] == "motion":
            icon = "mdi:adjust"
            devices.append(WattioBinarySensor(device["name"],
                                              "motion",
                                              icon,
                                              device["ieee"]
                                              ))
            _LOGGER.debug("Adding device: %s", device["name"])
    async_add_entities(devices)


class WattioBinarySensor(WattioDevice, BinarySensorDevice):
    """Representation of Sensor."""

    def __init__(self, name, devtype, icon, ieee):
        """Initialize the sensor."""
        self._pre = "bs_"
        self._name = name
        self._state = None
        self._icon = icon
        self._apidata = None
        self._ieee = ieee
        self._devtype = devtype
        self._battery = None
        self._data = None
        self._channel = None

    @property
    def available(self):
        """Return availability."""
        if self._data is not None:
            status = 0
            for device in self._data:
                if device["ieee"] == self._ieee:
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
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Return the image of the sensor."""
        return self._icon

    @property
    def is_on(self):
        """Return state of the sensor."""
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
        # Parece que no tira con las CONST devolver 0 o 1
        self._data = self.hass.data[DOMAIN]["data"]
        _LOGGER.error("ACTUALIZANDO SENSOR BINARIO %s - %s", self._name, self._ieee)
        if self._data is not None:
            for device in self._data:
                if device["ieee"] == self._ieee:
                    self._battery = device["status"]["battery"]
                    if device["type"] == "motion":
                        _LOGGER.debug(device["status"]["presence"])
                        self._state = device["status"]["presence"]
                    elif device["type"] == "door":
                        self._state = device["status"]["opened"]
                        _LOGGER.debug(device["status"]["opened"])
                    break
        # testvalue = self._wattiodata.update_data(hass, self._name, self._devtype, self._ieee)
            _LOGGER.debug(self._state)
            return self._state
        else:
            return False
