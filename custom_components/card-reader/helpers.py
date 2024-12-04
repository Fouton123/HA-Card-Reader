import sys
import glob
import serial

from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, MANUFACTURER, MODEL


def device_info(id):
    return DeviceInfo(
        identifiers={(DOMAIN, id)},
        manufacturer=MANUFACTURER,
        model=MODEL,
        name="Access Control",
    )
