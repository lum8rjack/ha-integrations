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

## stl_superpark

The STL Super Park integration displays the parking availability at the St. Louis Airport. The integration sends a GET request to `https://superparkinglot.com` every 15 minutes and parses the parking availability for each lot.

![stl_superpark](assets/stl_superpark.png)

- Copy the `stl_superpark` directory to the configuration folder `config/custom_components/`
- Add the integration to the yaml configuration file

```
sensor:
  - platform: stl_superpark
```

## Helpful Links

- https://developers.home-assistant.io/docs/core/entity/sensor
- https://dev.to/adafycheng/write-custom-component-for-home-assistant-4fce
