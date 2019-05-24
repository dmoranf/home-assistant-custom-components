""" Support for FortiGate Device Inventory table throught API """
import requests
import logging
import voluptuous as vol
from collections import namedtuple

""" Hassio includes """
import homeassistant.helpers.config_validation as cv
from homeassistant.components.device_tracker import (DOMAIN, PLATFORM_SCHEMA, DeviceScanner)
from homeassistant.const import CONF_FILENAME,CONF_HOST, CONF_PASSWORD, CONF_USERNAME, CONF_PORT, CONF_TIMEOUT

""" Hassio Schema definitions """
PLATFORM_SCHEMA = vol.All(
    PLATFORM_SCHEMA.extend({
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Optional(CONF_PASSWORD, default=''): cv.string,
        vol.Optional(CONF_PORT, default=443): cv.port,
        vol.Optional(CONF_TIMEOUT, default=60): cv.positive_int,
    })
)

_LOGGER = logging.getLogger(__name__)

Device = namedtuple('Device', ['mac', 'name', 'ip', 'last_update'])

""" Config vars (No changes needed!) """
FORTI_DEVICE_URI = '/api/v2/monitor/user/device/select/'


def get_scanner(hass, config):
    """Validate the configuration and return a FortiOS scanner."""
    return FortigateDeviceTracker(config[DOMAIN])
    
class FortigateAPI:
    def __init__(self,host,port,username,password,timeout=60):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._timeout = timeout
        self._session = None
        self.login()
    
    def __del__(self):
        if self._session is not None:
            self.logout()

    def login(self):
        self._session = requests.session()
        try:
            login_uri = "https://{}:{}/logincheck".format(self._host,self._port)
            res=self._session.post(login_uri,
                    data='username={}&secretkey={}&ajax=1'.format(self._username,self._password),
                    verify = False,
                    timeout = self._timeout)
            _LOGGER.debug("Login request status code: %s" %(res.status_code))
            for cookie in self._session.cookies:
                if cookie.name == "ccsrftoken":
                    csrftoken = cookie.value[1:-1]
                    self._session.headers.update({'X-CSRFTOKEN':csrftoken})
                    _LOGGER.debug("Cookie established")
        except:
            _LOGGER.error("Could not connect to %s" %(login_uri))
            self._session = None
            return False
        
    def logout(self):
        logout_uri = "https://{}:{}/logout".format(self._host,self._port)
        self._session.get(logout_uri,verify = False, timeout = self._timeout)
        _LOGGER.debug("Session logged out")

    def get_devices(self):
        device_uri = "https://{}:{}{}".format(self._host,self._port,FORTI_DEVICE_URI)
        if self._session is not None:
            request = self._session.get (device_uri, verify = False, timeout = self._timeout)        
            if request.status_code == 200:
                return request.json()['results']
            else:
                _LOGGER.error("Could'n get devices from Fortigate, request status code %s" %(request.status_code))
                return None
        else:
            return None

class FortigateDeviceTracker(DeviceScanner):
    def __init__(self,config):
        self._host = config[CONF_HOST]
        self._username = config[CONF_USERNAME]
        self._password = config[CONF_PASSWORD]
        self._port = config[CONF_PORT]
        self.last_results = []
        self._timeout = config[CONF_TIMEOUT]
           

    def scan_devices(self):
        self._update_info()
        return [device.mac for device in self.last_results]

    def get_device_name(self,device):
        name = [result.name for result in self.last_results if result.mac == device]
        return name[0]

    def get_extra_attributes(self,device):
        filter_ip = next (( result.ip for result in self.last_results if result.mac == device), None)
        return {'ip': filter_ip }


    def _update_info(self):
        self.last_results=[]
        fortigate = FortigateAPI(self._host,self._port,self._username,self._password,self._timeout)
        devices = fortigate.get_devices()
        if devices is not None:
            """ Resultados """
            for device in devices:
                try: 
                    name = device["host"]["name"] 
                except:
                    name = device["mac"].upper()
                try:
                    ip = device["addr"] 
                except:
                    ip = None
                if int(device["last_seen"]) < self._timeout:
                    if device["mac"] is None:
                        _LOGGER.error(device)
                        continue
                    _LOGGER.debug("Add device %s - %s - last seen: %s" %(device["mac"],name,device["last_seen"]))
                    self.last_results.append(Device(device["mac"].upper(),name,ip,device["last_seen"]))   
                else:
                    _LOGGER.debug("Ignoring device %s - %s - last seen: %s" %(device["mac"],name,device["last_seen"]))
            del fortigate
            return True
        del fortigate
        return False

