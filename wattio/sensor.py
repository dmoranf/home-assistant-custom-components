""" Platform for Wattio integration testing """
import logging
import os
import requests
import json

""" Custom imports """
from . import wattioAPI,WattioRegisterView,check_config_file
from . import (ATTR_ACCESS_TOKEN, ATTR_CLIENT_ID, ATTR_LAST_SAVED_AT,WATTIO_CONF_FILE,
				WATTIO_AUTH_CALLBACK_PATH,WATTIO_AUTH_START,WATTIO_AUTH_URI,WATTIO_TOKEN_URI,
				DEFAULT_CONFIG)

""" HASSIO imports """
import homeassistant.helpers.config_validation as cv
from homeassistant.core import callback
from homeassistant.util.json import load_json, save_json
from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.entity import Entity
#from homeassistant.const import STATE_UNKNOWN
from homeassistant.const import TEMP_CELSIUS
from homeassistant.const import (CONF_SCAN_INTERVAL)


_LOGGER = logging.getLogger(__name__)
_CONFIGURING = {}



def get_auth_uri(hass,client_id):
	state = "WATTIOHASSIOTESTING2" # Change to RANDOM
	redirect_uri = '{}{}'.format(hass.config.api.base_url,WATTIO_AUTH_START)
	authorize_uri = WATTIO_AUTH_URI+'?response_type=code&client_id='+client_id+'&redirect_uri='+redirect_uri
	return authorize_uri

def request_app_setup(hass, config, add_devices,add_entities, config_path, discovery_info=None):
    configurator = hass.components.configurator

    def wattio_configuration_callback(callback_data):
        config_path = hass.config.path(WATTIO_CONF_FILE)
        config_status = check_config_file(config_path)
        if config_status == 2:
            return False
        elif config_status == 1:
            configurator.notify_errors(_CONFIGURING['wattio'],"test")
            return False
        else:
            setup_platform(hass, config, add_devices, add_entities)

    start_url = "{}{}".format(hass.config.api.base_url,WATTIO_AUTH_CALLBACK_PATH)
    description = 'Wattio SmartHome no configurado</span>.<br /><br /> - Solicita tu Client y Secret ID a soporte de Wattio.<br />- Añ&aacute;delo al fichero wattio.conf<br /><br />Si algo no va bien revisa los logs :)<br />'
    submit = "Siguiente"
    _CONFIGURING['wattio'] = configurator.request_config('Wattio', wattio_configuration_callback,description=description, submit_caption=submit)

def request_oauth_completion(hass,config,add_devices,add_entities,auth_uri,discovery_info=None):
    """Request user complete WATTIO OAuth2 flow."""
    configurator = hass.components.configurator

    def wattio_configuration_callback(callback_data):
        config_path = hass.config.path(WATTIO_CONF_FILE)
        config_file = load_json(config_path)
        token = config_file.get(ATTR_ACCESS_TOKEN)
        if token is None:
           return False
        else:
           setup_platform(hass, config, add_devices, add_entities)


    if "wattio" in _CONFIGURING:
        configurator.notify_errors(_CONFIGURING['wattio'],"Fallo el registro, intentalo de nuevo.")
        return

    start_url = '{}{}'.format(hass.config.api.base_url, WATTIO_AUTH_START)
    description = 'Para finalizar autoriza el componente en Wattio:<br /><br /> <a href="{}" target="_blank">{}</a>'.format(start_url,start_url)
    _CONFIGURING['wattio'] = configurator.request_config('Wattio',wattio_configuration_callback,description=description,submit_caption="Finalizar")



def setup_platform(hass, config, add_devices, add_entities, discovery_info=None):
	_LOGGER.debug("Wattio Sensor component running ...")
	config_path = hass.config.path(WATTIO_CONF_FILE)
	interval = config.get(CONF_SCAN_INTERVAL)
	_LOGGER.debug("Wattio config file: %s" %(config_path))
	config_status = check_config_file(config_path)
	if config_status == 2:
		request_app_setup(hass, config, add_devices,add_entities, config_path, discovery_info=None)
		return False
	elif config_status ==1:
		_LOGGER.error("Config file doesn't exist, creating ...")
		save_json(config_path, DEFAULT_CONFIG)
		request_app_setup( hass, config, add_devices,add_entities, config_path, discovery_info=None)
		return False
	if "wattio" in _CONFIGURING:
        	hass.components.configurator.request_done(_CONFIGURING.pop("wattio"))

	config_file = load_json(config_path)
	token = config_file.get(ATTR_ACCESS_TOKEN)
	#expires_at = config_file.get(ATTR_LAST_SAVED_AT)
	if token is not None:
		apidata = wattioAPI(config.get(CONF_SCAN_INTERVAL),token)
		registered_devices = apidata.get_devices()
		dev = []
		""" Create Updater Object """
		for device in registered_devices:
			measurement = None
			icon = None
			if device["type"] == "pod":
				icon = "mdi:power-socket-eu"
				measurement = "Watt"
				add_devices([WattioSensor(device["name"],device["type"],measurement,icon,apidata,device["ieee"])], True)
			if device["type"] == "bat":
				measurement = "Watt"
				add_devices([WattioSensor(device["name"],device["type"],measurement,icon,apidata,device["ieee"],device["channel"])], True)
			if device["type"] == "therm":
				measurement = TEMP_CELSIUS
				add_devices([WattioSensor(device["name"],device["type"],measurement,icon,apidata,device["ieee"])], True)
			if device["type"] == "motion":
				measurement = TEMP_CELSIUS
				add_devices([WattioSensor(device["name"],device["type"],measurement,icon,apidata,device["ieee"])], True)
			''' Not implemented right now 
			if device["type"] == "door":
				icon = "mdi:door"
				#add_devices([WattioSensor(device["name"],measurement,icon)], True)	
			'''
			_LOGGER.debug("Adding device: %s" %(device["name"]))	
	else:
		auth_uri = get_auth_uri(hass,config_file.get("client_id"))
		_LOGGER.error("No token configured, complete OAUTH2 authorization: %s" %(auth_uri))
		hass.http.register_view(WattioRegisterView(hass,config,add_entities,config_file.get("client_id"),config_file.get("client_secret"),auth_uri))
		request_oauth_completion(hass,config,add_devices,add_entities,auth_uri)



class WattioSensor(Entity):
	""" Representation of Sensor """
	def __init__(self, name, devtype, measurement,icon,apidata,ieee,channel=None):
		"""Initialize the sensor."""
		self._name = name
		self._state = None
		self._measurement = measurement
		self._icon = icon
		self._apidata = apidata
		self._ieee = ieee
		self._devtype = devtype
		self._channel = None
		if channel is not None:
			self._channel = channel-1
		#self.type = resource_type
		#self.update()

	@property
	def name(self):
		"""Return the name of the sensor."""
		return self._name

	@property
	def unit_of_measurement(self):
		return self._measurement

	@property
	def icon(self):
		return self._icon

	@property
	def state(self):
		return self._state

	def update(self):
		sensorvalue = self._apidata.update_data(self._name,self._devtype,self._ieee,self._channel)
		_LOGGER.debug("Updating sensor %s: %s" %(self._name,sensorvalue))
		self._state = sensorvalue