# Home-Assistant Custom Components
This information is also available in [English](./README.md)

Componentes
------------
   * [fortigate device tracker](#Fortigate-Device-Tracker): Integración con Fortigate Device detection vía WEB-API.
   
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

 - Testeado en FortiOS 6.0.4
 - Descubrimiento de dispositivos habilitado en el Fortigate a nivel de Interface.

### Instalación

- Copiar el directorio "fortigate" a la carpeta de componentes personalizados: `<config dir>/custom_components/fortigate_tracker`
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
    
```

Variables:

- **host**: Dirección IP o nombre del interface de gestión del dispositivo Fortigate.
- **port** (*Opcional*): Puerto del servicio https (443 por defecto).
- **username**: Usuario con permisos de acceso a la API del fortigate.
- **password**: Contraseña de acceso.
- **consider_home**: (*Opcional*) Tiempo máximo durante el cual el dispositivo no se ha detectado y se marca como fuera.
- **interval_seconds**: (*Opcional*) Tiempo entre peticiones a la API del equipo Fortinet.

### Créditos

 - [FortiOS Tracker](https://community.home-assistant.io/t/fortios-device-tracker/28333/4) de [Mister_Slowhand](https://community.home-assistant.io/u/Mister_Slowhand): FortiOS Device Tracker mediante tabla ARP y SSH


