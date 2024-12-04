import voluptuous as vol
import secrets

from homeassistant import config_entries
from homeassistant.const import CONF_IP_ADDRESS, CONF_DEVICE_ID
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN


class AccessFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow."""

    def __init__(self):
        """Initialize the config flow."""
        self.device_config = {}

    async def async_step_user(self, user_input=None):
        """Handle config flow."""
        errors = {}

        if user_input is not None:
            ip = user_input[CONF_IP_ADDRESS]
            sn = user_input[CONF_DEVICE_ID]

            # Only a single instance of the integration
            if self._async_current_entries():
                return self.async_abort(reason="single_instance_allowed")

            my_id = secrets.token_hex(6)
            await self.async_set_unique_id(my_id)

            self._abort_if_unique_id_configured(
                updates={
                    ip: user_input[CONF_IP_ADDRESS],
                    sn: user_input[CONF_DEVICE_ID],
                }
            )

            self.device_config = {
                CONF_IP_ADDRESS: ip,
                CONF_DEVICE_ID: sn,
            }

            return await self._create_entry("Access Control")

        data = {
            vol.Required(CONF_IP_ADDRESS): str,
            vol.Required(CONF_DEVICE_ID): int,
        }

        return self.async_show_form(
            step_id="user",
            description_placeholders=self.device_config,
            data_schema=vol.Schema(data),
            errors=errors,
        )

    async def _create_entry(self, server_name):
        """Create entry for device."""
        return self.async_create_entry(title=server_name, data=self.device_config)
