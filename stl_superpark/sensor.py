"""Sensor for displaying the parking availability at the STL airport"""
from __future__ import annotations
from datetime import timedelta
import requests
import voluptuous as vol
import logging

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "STL Super Park"
DEFAULT_URL = "https://countsstl.abacusai.app/api/counts"
SCAN_INTERVAL = timedelta(minutes=15)

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
        # Set headers
        custom_headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36","Accept-Lanugage": "en-US,en;q=0.9"}

        # Send request
        response = requests.get(DEFAULT_URL, headers=custom_headers, timeout=5.0)
        response.raise_for_status()

        # Parse JSON directly to a Python dictionary
        data = response.json()

        # Get data for each lot
        lots = {lot["lot"]: lot for lot in data}

        # Example response
        """
        [
            {
                "lot": "Lot C",
                "capacity": 3019,
                "avail": 1000
            },
            {
                "lot": "Lot E",
                "capacity": 233,
                "avail": 52
            },
            {
                "lot": "Term 2",
                "capacity": 975,
                "avail": -7
            },
            {
                "lot": "Term 1",
                "capacity": 1850,
                "avail": 663
            },
            {
                "lot": "Lot B",
                "capacity": 481,
                "avail": 63
            },
            {
                "lot": "Lot A",
                "capacity": 973,
                "avail": 294
            },
            {
                "lot": "Lot D",
                "capacity": 1310,
                "avail": 68
            }
        ]
        """

        # Calculate % available for each lot
        self.spaces["t1"] = str(int((lots["Term 1"]["avail"] / lots["Term 1"]["capacity"]) * 100))
        self.spaces["t2"] = str(int((lots["Term 2"]["avail"] / lots["Term 2"]["capacity"]) * 100))
        self.spaces["a"] = str(int((lots["Lot A"]["avail"] / lots["Lot A"]["capacity"]) * 100))
        self.spaces["b"] = str(int((lots["Lot B"]["avail"] / lots["Lot B"]["capacity"]) * 100))
        self.spaces["c"] = str(int((lots["Lot C"]["avail"] / lots["Lot C"]["capacity"]) * 100))
        self.spaces["d"] = str(int((lots["Lot D"]["avail"] / lots["Lot D"]["capacity"]) * 100))
        self.spaces["e"] = str(int((lots["Lot E"]["avail"] / lots["Lot E"]["capacity"]) * 100))
