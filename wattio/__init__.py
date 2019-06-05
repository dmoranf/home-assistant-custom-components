""""Wattio integration."""
import logging
import os
from datetime import timedelta
from datetime import datetime
import json
import time
import requests
from aiohttp import web

from homeassistant.util.json import load_json, save_json
from homeassistant.core import callback
from homeassistant.const import (CONF_SCAN_INTERVAL)
from homeassistant.components.http import HomeAssistantView

ATTR_ACCESS_TOKEN = 'access_token'
ATTR_CLIENT_ID = 'client_id'
ATTR_CLIENT_SECRET = 'client_secret'
ATTR_LAST_SAVED_AT = 'last_saved_at'

WATTIO_STATUS_URI = 'https://api.wattio.com/public/v1/appliances/status'
WATTIO_DEVICES_URI = 'https://api.wattio.com/public/v1/appliances'
WATTIO_TOKEN_URI = 'https://api.wattio.com/public/oauth2/token'
WATTIO_POD_URI = 'https://api.wattio.com/public/v1/appliances/pod/{}/{}'
WATTIO_AUTH_URI = 'https://api.wattio.com/public/oauth2/authorize'
WATTIO_TOKEN_URI = 'https://api.wattio.com/public/oauth2/token'
WATTIO_AUTH_START = '/api/wattio'
WATTIO_CONF_FILE = 'wattio.conf'
WATTIO_AUTH_CALLBACK_PATH = '/api/wattio/callback'
WATTIO_CONF_FILE = 'wattio.conf'

DEFAULT_CONFIG = {
    'client_id': 'CLIENT_ID_HERE',
    'client_secret': 'CLIENT_SECRET_HERE'
}

CONFIGURING = {}

_LOGGER = logging.getLogger(__name__)

def request_app_setup(hass, config, add_devices, add_entities, config_path, setup_platform, discovery_info=None):
    """Function for module configuration."""

    global CONFIGURING
    configurator = hass.components.configurator

    def wattio_configuration_callback(callback_data):
        config_status = check_config_file(hass.config.path(WATTIO_CONF_FILE))
        if config_status == 2:
            return False
        elif config_status == 1:
            configurator.notify_errors(CONFIGURING['wattio'], "test")
            return False
        else:
            setup_platform(hass, config, add_devices, add_entities)

    description = 'Wattio SmartHome no configurado</span>.<br /><br /> - Solicita tu Client y Secret ID a soporte de Wattio.<br />- Edita manualmente el fichero wattio.conf<br />- Añade el Client y Secret al fichero<br /><br />- Una vez finalizado, pulsa Siguiente<br /><br />Si algo no va bien revisa los logs de HA :)<br />'
    submit = "Siguiente"
    CONFIGURING['wattio'] = configurator.request_config('Wattio',
                                                        wattio_configuration_callback,
                                                        description=description,
                                                        submit_caption=submit)

def request_oauth_completion(hass, config, add_devices, add_entities, auth_uri, setup_platform, discovery_info=None):
    """Request user complete WATTIO OAuth2 flow."""

    global CONFIGURING
    configurator = hass.components.configurator

    def wattio_configuration_callback(callback_data):
        """Check if token is configured else show the notification"""
        config_file = load_json(hass.config.path(WATTIO_CONF_FILE))
        token = config_file.get(ATTR_ACCESS_TOKEN)
        if token is None:
            return False
        else:
            setup_platform(hass, config, add_devices, add_entities)


    if "wattio" in CONFIGURING:
        configurator.notify_errors(CONFIGURING['wattio'], "Fallo el registro, intentalo de nuevo.")
        return

    start_url = '{}{}'.format(hass.config.api.base_url, WATTIO_AUTH_START)
    description = 'Para finalizar autoriza el componente en Wattio:<br /><br /> <a href="{}" target="_blank">{}</a>'.format(start_url, start_url)
    CONFIGURING['wattio'] = configurator.request_config('Wattio',
                                                        wattio_configuration_callback,
                                                        description=description,
                                                        submit_caption="Finalizar")


def get_auth_uri(hass, client_id):
    """Returns Wattio Auth URI."""
    #state = "WATTIOHASSIOTESTING2" # Change to RANDOM
    redirect_uri = '{}{}'.format(hass.config.api.base_url, WATTIO_AUTH_START)
    authorize_uri = WATTIO_AUTH_URI+'?response_type=code&client_id='+client_id+'&redirect_uri='+redirect_uri
    return authorize_uri

def check_config_file(configpath):
    """Check if config file exists | 0 All OK | 1 File does not exist | 2 Not configued."""
    if os.path.isfile(configpath):
        try:
            config_file = load_json(configpath)
            if config_file == DEFAULT_CONFIG:
                _LOGGER.error("Wattio is not configured, check %s", configpath)
                return 2
            else:
                return 0
        except:
            _LOGGER.error("Can't read %s file, please check owner / permissions", configpath)
            return 2
    else:
        return 1

class WattioRegisterView(HomeAssistantView):
    """Register View for Oauth2 Authorization."""

    requires_auth = False
    url = WATTIO_AUTH_START
    requires_auth = False
    name = "api:wattio"

    def __init__(self, hass, config, add_entities, client_id, client_secret, auth_uri):
        self.config = config
        self.add_entities = add_entities
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_uri = auth_uri
        self.hass = hass
    @callback
    def get(self, request):
        """Oauth2 completion View."""
        data = request.query
        text = "<h2>WATTIO</h2>"
        # Check if TOKEN previously exists.
        config_file = load_json(self.hass.config.path(WATTIO_CONF_FILE))
        if "access_token" in config_file:
            text += "Acceso previamente autorizado, si necesitar volver a actualizarlo borra el fichero %s y vuelve a iniciar el proceso.". self.hass.config.path(WATTIO_CONF_FILE)
            return web.Response(text=text, content_type='text/html')
        elif data.get('code') is None:
            _LOGGER.error("SIN AUTORIZAR")
            text += '''<p>Por favor, <a href="{}">autoriza a Home Assistant</a> para que pueda acceder a la informacion de WATTIO</p>
                '''.format(self.auth_uri)
            return web.Response(text=text, content_type='text/html')
        else:
            api = wattioAPI(self.config.get(CONF_SCAN_INTERVAL))
            token = api.get_token(str(data.get('code')), str(self.client_id), str(self.client_secret))
            if token:
                config_contents = {ATTR_ACCESS_TOKEN: token,
                                   ATTR_CLIENT_ID: self.client_id,
                                   ATTR_CLIENT_SECRET: self.client_secret,
                                   ATTR_LAST_SAVED_AT: int(time.time())
                                  }
                try:
                    save_json(self.hass.config.path(WATTIO_CONF_FILE), config_contents)

                    return web.Response(text="Autorizado :)")
                except:
                    _LOGGER.error("Error guardando TOKEN %s ", sys.exc_info()[0])
                    return web.Response(text="No se ha podido almacenar TOKEN revisar permisos")


class wattioAPI:
    """Wattio API Class."""

    def __init__(self, interval, token=None):
        self._schedule = interval
        self._value = None
        self._data = None
        self._token = token
        self._updated = None

    def get_token(self, code, client_id, client_secret):
        """ Get Token from Wattio API, requieres Auth Code, Client ID and Secret """
        data = {'code' : code,
                'client_id' : client_id,
                'client_secret' : client_secret,
                'grant_type' : 'authorization_code',
                'redirect_uri' : 'http://192.168.0.250:8123'+WATTIO_AUTH_START
                }
        try:
            access_token_response = requests.post(WATTIO_TOKEN_URI, data=data, verify=False, allow_redirects=False)
            if "404" in access_token_response.text:
                _LOGGER.error("Token expired, restart the process")
                return 0
            try:
                token_json = json.loads(access_token_response.text)
                token = token_json["access_token"]
                self._token = token
                return token
            except:
                _LOGGER.error("Error getting token")
                return 0
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Could't get TOKEN from Wattio API")
            _LOGGER.error(err)

    def get_device_availability(self, ieee):
        """Get device availability."""
        if self._data is not None:
            _availability = False
            try:
                device_status = json.loads(self._data)
                for device in device_status:
                    if device["ieee"] == ieee:
                        _availability = True
            except:
                _LOGGER.error("API Data problems, couldn't check availability status")
        else:
            _LOGGER.error("No API DATA, couldn't check availability data for %s", ieee)
        if _availability:
            _LOGGER.debug("Device %s is available", ieee)
        else:
            _LOGGER.debug("Device %s is NOT available", ieee)
        return _availability

    def get_devices(self):
        """Get device info from Wattio API."""
        api_call_headers = {'Authorization': 'Bearer ' + self._token}
        try:
            api_call_response = requests.get(WATTIO_DEVICES_URI, headers=api_call_headers, verify=False)
            registered_devices = json.loads(api_call_response.text)
            return registered_devices
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Couldn't get device info from Wattio API")
            _LOGGER.error(err)
            return None

    def set_switch_status(self, ieee, status):
        """Change switch status on / off."""
        _LOGGER.error("Status change for %s - %s", str(ieee), str(status))
        _LOGGER.error("Peticion API")
        api_call_headers = {'Authorization': 'Bearer ' + self._token}
        try:
            uri = WATTIO_POD_URI.format(str(ieee), str(status))
            api_call_response = requests.put(uri, headers=api_call_headers, verify=False)
            _LOGGER.error(api_call_response.text)
            if status == "on":
                return 1
            else:
                return 0
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Couldn't change device status data from Wattio API")
            _LOGGER.error(err)


    def update_switch_status(self, name, devtype, ieee):
        """Get switch status (On/Off)."""
        _LOGGER.error("Updater request for %s", str(name))
        self.get_data()
        if devtype == "pod":
            device_status = json.loads(self._data)
            for device in device_status:
                if device["ieee"] == ieee:
                    return device["status"]["state"]
        else:
            return 0


    def update_data(self, name, devtype, ieee, channel=None):
        """Get status data from Wattio API."""
        minutes = self._schedule.total_seconds()/60
        # Check if update of cache is needed
        if self._updated is not None:
            nextupdate = self._updated + timedelta(minutes=int(minutes))
            _LOGGER.debug("Updated: %s - Next Update: %s", self._updated, nextupdate)
        if self._data is None or (self._updated is not None and datetime.now() >= nextupdate):
            self._updated = datetime.now()
            self.get_data()
        else:
            _LOGGER.debug("Update request for %s: Using cached data", str(name))
        if self._data is not None:
            device_status = json.loads(self._data)
            try:
                if channel is not None and devtype == "bat":
                    # BAT device get channel data
                    for device in device_status:
                        if device["ieee"] == ieee:
                            return  device["status"]["consumption"][channel]
                elif devtype == "therm":
                    # THERMIC data get current temp
                    for device in device_status:
                        if device["ieee"] == ieee:
                            return device["status"]["current"]
                elif devtype == "motion":
                    # MOTION data get current temp
                    for device in device_status:
                        if device["ieee"] == ieee:
                            return device["status"]["temperature"]
                elif devtype == "motionBinary":
                    # MOTION data get current presence
                    for device in device_status:
                        if device["ieee"] == ieee:
                            return device["status"]["presence"]
                elif devtype == "pod":
                    # POD data get current WAT consumption
                    for device in device_status:
                        if device["ieee"] == ieee:
                            return device["status"]["consumption"]
                elif devtype == "door":
                    # DOOR data get current status
                    for device in device_status:
                        if device["ieee"] == ieee:
                            return device["status"]["opened"]
                else:
                    # Other unknown devices return 0
                    return 0
            except Exception:
                _LOGGER.error("API had a problem and didn't return expected data ... ")

            return 0
        else:
            _LOGGER.error("API had a problem and didn't return any data ... ")
            return 0

    def get_data(self):
        """Get Data from WattioAPI."""
        _LOGGER.debug("Cache update is needed - New API request")
        api_call_headers = {'Authorization': 'Bearer ' + self._token}
        try:
            api_call_response = requests.get(WATTIO_STATUS_URI, headers=api_call_headers, verify=False)
            if api_call_response.status_code == 200:
                _LOGGER.debug("API call status code %s", api_call_response.status_code)
                self._data = api_call_response.text                
            else:
                _LOGGER.error("API call Status code %s", api_call_response.status_code)
                self._data = None
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Couldn't get device status data from Wattio API")
            _LOGGER.error(err)
            self._data = None
