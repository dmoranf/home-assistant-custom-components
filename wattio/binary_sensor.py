"""Platform for Wattio integration testing."""
import logging

from homeassistant.util.json import load_json, save_json
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.components.binary_sensor import BinarySensorDevice

from . import (wattioAPI, WattioRegisterView, check_config_file, get_auth_uri,
               request_app_setup, request_oauth_completion, ATTR_ACCESS_TOKEN,
               WATTIO_CONF_FILE, DEFAULT_CONFIG, CONFIGURING
               )

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, add_entities, discovery_info=None):
    """Wattio Sensor setup platform."""
    _LOGGER.debug("Wattio Binary Sensor component running ...")
    config_path = hass.config.path(WATTIO_CONF_FILE)
    _LOGGER.debug("Wattio config file: %s", config_path)
    config_status = check_config_file(config_path)
    # Check Wattio file configuration status
    if config_status == 2:
        request_app_setup(hass,
                          config,
                          add_devices,
                          add_entities,
                          config_path,
                          setup_platform,
                          discovery_info=None)
        return False
    elif config_status == 1:
        _LOGGER.error("Config file doesn't exist, creating ...")
        save_json(config_path, DEFAULT_CONFIG)
        request_app_setup(hass,
                          config,
                          add_devices,
                          add_entities,
                          config_path,
                          setup_platform,
                          discovery_info=None)
        return False
    if "wattio" in CONFIGURING:
        hass.components.configurator.request_done(CONFIGURING.pop("wattio"))

    config_file = load_json(config_path)
    token = config_file.get(ATTR_ACCESS_TOKEN)
    #Wattio Token does not expire
    #expires_at = config_file.get(ATTR_LAST_SAVED_AT)
    if token is not None:
        apidata = wattioAPI(config.get(CONF_SCAN_INTERVAL), token)
        registered_devices = apidata.get_devices()
        # Create Updater Object
        for device in registered_devices:
            icon = None
            if device["type"] == "door":
                icon = "mdi:door"
                add_devices([WattioBinarySensor(device["name"],
                                                device["type"],
                                                icon,
                                                apidata,
                                                device["ieee"]
                                                )], True)
                _LOGGER.debug("Adding device: %s", device["name"])
            if device["type"] == "motion":
                icon = "mdi:adjust"
                add_devices([WattioBinarySensor(device["name"],
                                                "motionBinary",
                                                icon,
                                                apidata,
                                                device["ieee"]
                                                )], True)
                _LOGGER.debug("Adding device: %s", device["name"])
    else:
        # Not Authorized, need to complete OAUTH2 process
        auth_uri = get_auth_uri(hass, config_file.get("client_id"))
        _LOGGER.error("No token configured, complete OAUTH2 authorization: %s", auth_uri)
        hass.http.register_view(WattioRegisterView(hass,
                                                   config,
                                                   add_entities,
                                                   config_file.get("client_id"),
                                                   config_file.get("client_secret"),
                                                   auth_uri))
        request_oauth_completion(hass, config, add_devices, add_entities, auth_uri, setup_platform)

class WattioBinarySensor(BinarySensorDevice):
    """Representation of Sensor."""

    def __init__(self, name, devtype, icon, apidata, ieee):
        """Initialize the sensor."""
        self._name = name
        self._state = None
        self._icon = icon
        self._apidata = apidata
        self._ieee = ieee
        self._devtype = devtype
        #self.type = resource_type
        #self.update()

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

    def update(self):
        """Update sensor data."""
        sensorvalue = self._apidata.update_data(self._name, self._devtype, self._ieee)
        _LOGGER.debug("Updating binary sensor %s: %s", self._name, sensorvalue)
        self._state = sensorvalue
