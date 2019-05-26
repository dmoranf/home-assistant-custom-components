# Home-Assistant Custom Components
This information is also available in [English](./README.md)

Componentes
------------
   * [fortigate device tracker](#Fortigate-Device-Tracker): Integración con Fortigate Device detection vía WEB-API.
   * [Wattio Smart Home](#Wattio-Smart-Home): Integración de la plataforma Wattio Smart Home vía WEB-API.   
----------------------------

## Fortigate Device Tracker
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

 - Testeado en FortiOS 6.0.4 y Home Assistant 0.90.2
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

- **host**: Dirección IP o nombre del interface de gestión del dispositivo Fortigate.
- **port** (*Opcional*): Puerto del servicio https (443 por defecto).
- **username**: Usuario con permisos de acceso a la API del fortigate.
- **password**: Contraseña de acceso.
- **consider_home**: (*Opcional*) Tiempo que debe transcurrir para marcar el dispositivo como "fuera" una vez marcado como offline (timeout).
- **interval_seconds**: (*Opcional*) Tiempo entre peticiones a la API del equipo Fortinet.
- **timeout**: (*Optional*) Tiempo para marcar el dispositivo como desconectado, en segundos (60 por defecto).
### Créditos

 - [FortiOS Tracker](https://community.home-assistant.io/t/fortios-device-tracker/28333/4) de [Mister_Slowhand](https://community.home-assistant.io/u/Mister_Slowhand): FortiOS Device Tracker mediante tabla ARP y SSH

### Wattio Smart Home

Integración de la plataforma Wattio Smart Home en Home Assistant a través de API. Este componente está en desarrollo, por favor, consulta el CHANGELOG.md para ver los últimos cambios.

### Requisitos

 - Client ID y Secret para usar la API de Wattio  (Solicitar a soporte de Wattio)
 - Testeado en Home Assistant 0.90.2

### Installación

- Copia la carpeta "wattio" al directorio `<config dir>/custom_components/wattio`.
- Configurar como se muestra más abajo.
- Reiniciar HASS.
- Seguir los pasos de configuración adicionales.

### Configuración

Añade la siguiente configuración al fichero `configuration.yaml`.

```yaml
# Wattio Sensors
sensor:
  - platform: wattio
    scan_interval: 300
```

Vars:
 - scan_interval: Intervalo de recolección de datos (y entre peticiones a la API)

### Pasos adicionales

 - Tras reiniciar Home Assistant, aparecerá una nueva notificación solicitando al usuario configurar el User ID y el Secret de la API. 
 - Una vez configurado, aparecerá una nueva notificación solicitando autorizar la aplicación en Wattio.
 - Seguir los enlaces, se redirigirá a una página de Wattio en la que solicitará usuario y contraseña. 
 - Finalmente, cerrar la notificación (Finalizar) y refrescar el GUI para ver los nuevos sensores Finally.

<p align="center">
<img src="https://raw.githubusercontent.com/dmoranf/home-assistant-custom-components/master/_screenshots/wattio_configuration.gif"></p>

