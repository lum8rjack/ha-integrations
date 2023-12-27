"""Sensor for displaying the user's public IP address."""
from __future__ import annotations

from datetime import timedelta

import requests

import voluptuous as vol

# Import the device class from the component that you want to support
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

DEFAULT_NAME = "Public IP"
DEFAULT_URL = "https://checkip.amazonaws.com"
SCAN_INTERVAL = timedelta(minutes=15)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})

# Setup the sensor
def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    # Get the name from the configuration
    name = config[CONF_NAME]

    add_entities([PublicIPSensor(name)], True)


class PublicIPSensor(SensorEntity):
    """Representation of the Public IP sensor."""

    _attr_attribution = "Public IP provided by AWS"
    _attr_icon = "mdi:ip"

    def __init__(self, name: str) -> None:
        """Initialize the Public IP sensor."""
        self._attr_name = name

    def ip(self) -> str:
        """Return the Public IP address"""
        return self.ip

    def update(self) -> None:
        """Get the latest data and updates the states."""
        ip = requests.get(DEFAULT_URL, timeout=2.50)
        self._attr_native_value = ip.text.strip()
