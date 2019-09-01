"""Platform for Wattio integration testing."""
import logging

from homeassistant.components.light import Light
from homeassistant.const import STATE_OK, STATE_ON, STATE_UNAVAILABLE

from . import DOMAIN, WattioDevice, wattioAPI


_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Wattio Sensor setup platform."""
    _LOGGER.debug("Wattio Switch component running ...")
    if discovery_info is None:
        _LOGGER.error("No Sensor(s) discovered")
        return
    devices = []
    # Create Updater Object
    for device in hass.data[DOMAIN]["devices"]:
        icon = None
        if device["type"] == "pod":
            devices.append(WattioSwitch(device["name"],
                                        device["type"],
                                        icon,
                                        device["ieee"]
                                        ))
            _LOGGER.debug("Adding device: %s", device["name"])
    async_add_entities(devices)


class WattioSwitch(WattioDevice, Light):
    """Representation of Sensor."""

    def __init__(self, name, devtype, icon, ieee):
        """Initialize the sensor."""
        self._pre = "sw_"
        self._name = name
        self._is_on = None
        self._state = None
        self._icon = icon
        self._ieee = ieee
        self._data = None
        self._devtype = devtype
        self._current_consumption = None
        self._channel = None

    @property
    def is_on(self):
        """Return is_on status."""
        return self._state

    async def async_turn_on(self):
        """Turn On method."""
        wattio = wattioAPI(self.hass.data[DOMAIN]["token"])
        _LOGGER.error("Encendiendo")
        wattio.set_switch_status(self._ieee, "on")
        self._state = STATE_ON
        return
        # return self._apidata.set_switch_status(self._ieee, "on", self.hass.[DOMAIN]["token"])

    async def async_turn_off(self):
        """Turn Off method."""
        wattio = wattioAPI(self.hass.data[DOMAIN]["token"])
        _LOGGER.error("Apagando")
        wattio.set_switch_status(self._ieee, "off")
        self._state = False
        return
        # return self._apidata.set_switch_status(self._ieee, "off", self.hass.[DOMAIN]["token"])

    @property
    def should_poll(self):
        """No polling needed."""
        return False

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
                if device["ieee"] == self._ieee:
                    status = 1
                    break
            if status == 1:
                _LOGGER.debug("Device %s - available", self._name)
                return STATE_OK
            else:
                _LOGGER.debug("Device %s - NOT available", self._name)
                return STATE_UNAVAILABLE

    async def async_update(self):
        """Return sensor state."""
        self._data = self.hass.data[DOMAIN]["data"]
        _LOGGER.error("ACTUALIZANDO SWITCH %s - %s", self._name, self._ieee)
        if self._data is not None:
            for device in self._data:
                if device["ieee"] == self._ieee:
                    _LOGGER.debug(device["status"]["state"])
                    if device["status"]["state"] == 1:
                        self._state = STATE_ON
                    else:
                        self._state = False
                    break
        # testvalue = self._wattiodata.update_data(hass, self._name, self._devtype, self._ieee)
            _LOGGER.debug(self._state)
            return self._state
        else:
            return False
