# ha-integrations
Custom Home Assistant integrations

## public_ip

The Public IP integration displays the Home Assistant's public IP address. The integration sends a GET request to `https://checkip.amazonaws.com` every 15 minutes to check if the IP has changed.

![public_ip](assets/public_ip.png)

- Copy the `public_ip` directory to the configuration folder `config/custom_components/`
- Add the integration to the yaml configuration file

```
sensor:
  - platform: public_ip
```

## Helpful Links

- https://developers.home-assistant.io/docs/core/entity/sensor
- https://dev.to/adafycheng/write-custom-component-for-home-assistant-4fce
