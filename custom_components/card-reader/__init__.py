from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_IP_ADDRESS, CONF_DEVICE_ID
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, MANUFACTURER, MODEL

ATTRIBUTION = "Access Control"
DEFAULT_BRAND = "RFID"

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up the Agent component."""
    hass.data.setdefault(DOMAIN, {})

    device_registry = dr.async_get(hass)

    device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        identifiers={(DOMAIN, config_entry.entry_id)},
        manufacturer=MANUFACTURER,
        model=MODEL,
        name="Access Control",
        sw_version=0.1,
    )

    ip = config_entry.data[CONF_IP_ADDRESS]
    sn = config_entry.data[CONF_DEVICE_ID]
    
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(
        config_entry, PLATFORMS
    )

    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok
