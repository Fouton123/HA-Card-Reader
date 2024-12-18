"""Support for reading data from a serial port."""

from __future__ import annotations
import json
import logging
from pathlib import Path
from datetime import timedelta

import asyncudp
import binascii

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS, CONF_DEVICE_ID
from homeassistant.core import callback
from homeassistant.util import dt

from .const import DOMAIN

from .helpers import device_info

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=1)
RECV_PORT = 51707
SEND_PORT = 60000


async def async_setup_entry(
    hass, config_entry, async_add_entities, discovery_info=None
):
    """Set up the Serial sensor platform."""
    ip = config_entry.data[CONF_IP_ADDRESS]
    sn = config_entry.data[CONF_DEVICE_ID]
    device_id = config_entry.entry_id
    access = AccessSensor(ip, sn, device_id)

    sensors = [access]

    async_add_entities(sensors, True)


class AccessSensor(SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, ip, sn, device_id):
        self._attr_name = "Reader"
        unique_id = f"reader_{sn}"
        self._attr_unique_id = unique_id
        self._attr_device_info = device_info(device_id)
        self._icon = "mdi:badge-account-outline"
        self._state = None
        self._prev_state = None
        self._udp = None
        self._query = None

        self._sn = self.get_sn(sn)
        self._addr = (ip, SEND_PORT)

        self.init_comm()

    async def async_update(self):
        if self._udp is None:
            self.open_socket()

        if self._query is not None:
            self._udp.sendto(self._query, self._addr)
            try:
                message, address = self._udp.recvfrom(1024)
                badge = await self.process_msg(message)
            except:
                badge = self._state
                
        if self._prev_state != badge:
            self._prev_state = badge
            self._state = badge

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return self._icon

    def open_socket(self):
        #self._udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self._udp.bind(('192.168.20.203', RECV_PORT))
        #self._udp.settimeout(2)
        self._udp = await asyncudp.create_socket(local_addr=('192.168.20.203', RECV_PORT))

    def init_comm(self):
        if self._udp is None:
            self.open_socket()
        dat = (b"~" + self._sn + b"\x81\x10:\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00;\x02\r")
        self._udp.sendto(dat, self._addr)
        try:
            message, address = self._udp.recvfrom(1024)
            self.process_msg(message)
        except:
            pass


    def process_msg(self, message):
        tmp = []
        for i in message:
            tmp.append(hex(i)[2:].zfill(2))

        index_one = int(tmp[12], 16) + 1
        index_one = hex(index_one)[2:].zfill(2)

        index_two = int(tmp[12], 16) + 2
        index_two = hex(index_two)[2:].zfill(2)

        self._query = b'~' + self._sn + b'\x81\x10' + binascii.a2b_hex(index_one) + b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' + binascii.a2b_hex(index_two) + b'\x02\r'

        return f'{tmp[17]}{tmp[18]}{tmp[19]}'

    def get_sn(self, serial):
        hex_sn = f"{hex(serial)[4:]}{hex(serial)[2:-2]}"
        return binascii.a2b_hex(hex_sn)
