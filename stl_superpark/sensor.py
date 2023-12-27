"""Sensor for displaying the parking availability at the STL airport"""
from __future__ import annotations
from datetime import timedelta
import requests
from lxml import html
import voluptuous as vol
import logging

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "STL Super Park"
DEFAULT_URL = "https://superparkinglot.com/"
SCAN_INTERVAL = timedelta(minutes=15)
LOCATION_DICTIONARY = {
    "Terminal 1": "//a[@href='https://superparkinglot.com/terminal-1']/div/p[@class='availability']/text()",
    "Terminal 2": "//a[@href='https://superparkinglot.com/terminal-2']/div/p[@class='availability']/text()",
    "Lot A": "//a[@href='https://superparkinglot.com/lot-a']/div/p[@class='availability']/text()",
    "Lot B": "//a[@href='https://superparkinglot.com/lot-b']/div/p[@class='availability']/text()",
    "Lot C": "//a[@href='https://superparkinglot.com/lot-c']/div/p[@class='availability']/text()",
    "Lot D": "//a[@href='https://superparkinglot.com/lot-d']/div/p[@class='availability']/text()",
    "Lot E": "//a[@href='https://superparkinglot.com/lot-e']/div/p[@class='availability']/text()"
}

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})

# Setup the sensor
async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    
    # Get the name from the configuration
    name = config[CONF_NAME]
    stl_data = STLSuperParkData(hass)
    await stl_data.async_update()

    sensors = [
        STLSuperParkSensor(stl_data, name, "t1"),
        STLSuperParkSensor(stl_data, name, "t2"),
        STLSuperParkSensor(stl_data, name, "a"),
        STLSuperParkSensor(stl_data, name, "b"),
        STLSuperParkSensor(stl_data, name, "c"),
        STLSuperParkSensor(stl_data, name, "d"),
        STLSuperParkSensor(stl_data, name, "e"),
        ]
    
    async_add_entities(sensors, True)

class STLSuperParkSensor(Entity):
    """Representation of a STL Parking sensor."""

    def __init__(self, parkingdata: STLSuperParkData, name: str, key: str) -> None:
        self._name = name
        self._condition = key
        self._condition_name = key.upper()
        self._unit_of_measurement = "%"
        self._icon = "mdi:parking"
        self.parkingdata = parkingdata
        self._state = "0"

    @property
    def name(self):
        """Return the name of the sensor."""
        return "{} {}".format(self._name, self._condition_name)
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon
    
    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unit_of_measurement

    async def async_update(self):
        """Get the latest data."""
        await self.parkingdata.async_update()
        self._state = self.parkingdata.spaces[self._condition]


class STLSuperParkData:
    def __init__(self, hass):
        self.hass = hass
        self.spaces = {
            "t1" : "0",
            "t2" : "0",
            "a" : "0",
            "b" : "0",
            "c" : "0",
            "d" : "0",
            "e" : "0",
        }

    @Throttle(SCAN_INTERVAL)
    async def async_update(self):
        try:
            await self.hass.async_add_executor_job(self.update)

        except Exception as ex:
            _LOGGER.error(f"Error getting STL Parking data: {ex}")

    def update(self):
        page = requests.get(DEFAULT_URL, timeout=2.50)
        tree = html.fromstring(page.content)

        # Get element using XPath
        for key, value in LOCATION_DICTIONARY.items():
            availability = tree.xpath(value)
            percent = availability[0]

            if "Terminal 1" == key:
                self.spaces["t1"] = percent.strip()
            elif "Terminal 2" == key:
                self.spaces["t2"] = percent.strip()
            elif "Lot A" == key:
                self.spaces["a"] = percent.strip()
            elif "Lot B" == key:
                self.spaces["b"] = percent.strip()
            elif "Lot C" == key:
                self.spaces["c"] = percent.strip()
            elif "Lot D" == key:
                self.spaces["d"] = percent.strip()
            elif "Lot E" == key:
                self.spaces["e"] = percent.strip()
