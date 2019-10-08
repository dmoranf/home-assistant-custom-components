# Home-Assistant Custom Components
This information is also available in [English](./README.md)

Componentes
------------
   * [fortigate device tracker](#Fortigate-Device-Tracker): Integración con Fortigate Device detection vía WEB-API.
   * [Wattio Smart Home](#Wattio-Smart-Home): Integración de la plataforma Wattio Smart Home vía WEB-API.   
----------------------------

## Fortigate Device Tracker
<img src="https://img.shields.io/badge/Version-0.1.3-green.svg" />

Esta solución se basa en el descubrimiento de dispositivos en base a la información que el propio firewall Fortigate genera mediante descubrimiento y análisis del tráfico.

El inventario de dispositivos se encuentra bajo el menú  `User & Device -> Device inventory`:


<p align="center">
<img src="https://raw.githubusercontent.com/dmoranf/home-assistant-custom-components/master/_screenshots/fortigate_device_detection.png" width="600px"></p>


El firewall para determinar si un dispositivo está activo o no se basa en un timeout establecido, por defecto, en 5 minutos y que es configurable vía CLI:

```
config system global
set device-idle-timeout 300
end
```

No obstante desde la API dicho valor **no se devuelve**, y se obtiene un LAST_SEEN, por lo que aplican los tiempos configurados en HASS. Para que los datos sean consistentes entre ambos, el parámetro *device-idle-timeout* del firewall y el *consider_home* de HASS deberían ser similares.

### Requisitos

 - Testeado en FortiOS 6.0.4 y Home Assistant >= 0.90.2 (Testeado con 0.98.2)
 - Descubrimiento de dispositivos habilitado en el Fortigate a nivel de Interface.

### Instalación

- Copiar el directorio "fortigate_tracker" a la carpeta de componentes personalizados: `<config dir>/custom_components/fortigate_tracker`
- Configurar como se muestra en el siguiente apartado.
- Reiniciar HASS.

### Configuración

Añadir la siguiente configuración al fichero `configuration.yaml`

```yaml
# Fortigate DeviceTracker
device_tracker:
  - platform: fortigate_tracker
    host: HOST
    port: HTTPS_PORT
    username: !secret FG_USERNAME
    password: !secret FG_PASSWORD
    consider_home: 300
    interval_seconds: 120
    timeout: 120
    
```

Variables:

| Variable | Descripción |
| --- | --- | 
| **host** | Dirección IP o nombre del interface de gestión del dispositivo Fortigate. |
| **port** | (*Opcional*): Puerto del servicio https (443 por defecto). | 
| **username** | Usuario con permisos de acceso a la API del fortigate. |
| **password** | Contraseña de acceso. | 
| **consider_home** | (*Opcional*) Tiempo que debe transcurrir para marcar el dispositivo como "fuera" una vez marcado como offline (timeout). |
| **interval_seconds** | (*Opcional*) Tiempo entre peticiones a la API del equipo Fortinet. | 
| **timeout** | (*Optional*) Tiempo para marcar el dispositivo como desconectado, en segundos (60 por defecto). |

### Créditos

 - [FortiOS Tracker](https://community.home-assistant.io/t/fortios-device-tracker/28333/4) de [Mister_Slowhand](https://community.home-assistant.io/u/Mister_Slowhand): FortiOS Device Tracker mediante tabla ARP y SSH

## Wattio Smart Home
<img src="https://img.shields.io/badge/Version-0.2.3-green.svg" />

Integración de la plataforma Wattio Smart Home en Home Assistant a través de API. Este componente está en desarrollo, por favor, consulta el [CHANGELOG.md](https://github.com/dmoranf/home-assistant-custom-components/blob/master/wattio/CHANGELOG.md) para ver los últimos cambios.

Link: [Wattio SmartHome](https://wattio.com)

Más información: [Foro](https://community.wattio.com/portal/community/topic/integrar-wattio-con-home-assistant)

### Información importante

Desde la versión 0.96 ha cambiado la implementacion de los termostatos y no es compatible con versiones anteriores, la versión por defecto es compatible con >= 0.96, pero se incluye un fichero climate.py.pre_096 (no mantenido) que sería compatible con las versiones 0.92 a 0.96. En caso de necesitar usarlo, haz copia de climate.py y renombra cliamte.py_pre_096 a climate.py.

### Capturas de Pantalla

 - Sensores Wattio  (Ejemplos de Bat & Thermic):

<p align="center">
<img src="https://raw.githubusercontent.com/dmoranf/home-assistant-custom-components/master/_screenshots/wattio_bat_sensor.png" width="300px">   &nbsp;&nbsp;  <img src="https://raw.githubusercontent.com/dmoranf/home-assistant-custom-components/master/_screenshots/wattio_thermic_sensor.png" width="300px"></p>

- Sensores Binarios Wattio (Ejemplo de Door):

<p align="center">
<img src="https://raw.githubusercontent.com/dmoranf/home-assistant-custom-components/master/_screenshots/wattio_door_sensor.png" width="300px"></p>

- Switch de Wattio (Ejemplo de Pod):

<p align="center">
<img src="https://raw.githubusercontent.com/dmoranf/home-assistant-custom-components/master/_screenshots/wattio_pod_switch.png" width="300px"></p>

### Requisitos

 - Client ID y Secret para usar la API de Wattio  (Solicitar a soporte de Wattio)
 - Home Assistant >= 0.90.2 (Testeado con 0.98.2)

### Instalación

- Copia la carpeta "wattio" al directorio `<config dir>/custom_components/wattio`.
- Configurar como se muestra más abajo.
- Reiniciar HASS.
- Seguir los pasos de configuración adicionales.

### Configuración

Añade la siguiente configuración al fichero `configuration.yaml`.

> Desde la versión 0.2.0 se ha cambiado la implementación del componente. Si estás actualizando desde una versión anterior **es NECESARIO CAMBIAR LA CONFIGURACION del fichero **

```yaml
# Configuración plataforma WATTIO
wattio:
    scan_interval: 60
    therm_max_temp: 30
    therm_min_temp: 10 
    security: true
    security_interval: 300
```
Variables:

| Variable | Descripción |
| --- | --- |
| *scan_interval* | OPCIONAL - Intervalo de recolección de datos en segundos , por defecto 30 segundos |
| *therm_max_temp* | OPCIONAL - Temperatura máxima configurable para el thermic, por defecto 30 grados |
| *therm_min_temp* | OPCIONAL - Temperatura mínima configurable para el thermic, por defecto 10 grados |
| *security* | OPCIONAL - Habilitar los dispositivos de seguridad, por defecto false |
| *security_interval* | OPCIONAL - Intervalo de recolección de datos en segundos, por defecto scan_interval |


### Pasos adicionales

 - Tras reiniciar Home Assistant, aparecerá una nueva notificación solicitando al usuario configurar el User ID y el Secret de la API.
 - Se creará el fichero de configuración "wattio.conf" de forma automática.
 - Es necesario modificar el fichero "wattio.conf" y añadir el user id y secret. 
   
   > El soporte de Wattio deberá facilitarte el user id y secret. Estas credenciales NO son tu usuario y contraseña de acceso   

 - Una vez configurado, aparecerá una nueva notificación solicitando autorizar la aplicación en Wattio.
 - Seguir los enlaces, se redirigirá a una página de Wattio en la que solicitará usuario y contraseña. 
 - Finalmente, cerrar la notificación (Finalizar) y refrescar el GUI para ver los nuevos sensores.
 - Una vez añadidos los sensores, estos comenzarán a obtener datos según el intervalo configurado.


<p align="center">
<img src="https://raw.githubusercontent.com/dmoranf/home-assistant-custom-components/master/_screenshots/wattio_config.gif"></p>

