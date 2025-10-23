"""Configuration flow for the Energy Stats integration."""

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import DOMAIN, SENSOR_KEYS

_LOGGER = logging.getLogger(__name__)


class EnergyStatsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow class for Energy Stats integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, vol.Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Execute main configuraton step."""
        _LOGGER.debug("Executing async_step_user...")
        errors = {}
        if user_input is not None:
            _LOGGER.debug("Processing user input...")
            data = {k: user_input.get(k) for k in SENSOR_KEYS}
            data["identifier"] = user_input.get("identifier")

            if self.source == config_entries.SOURCE_RECONFIGURE:
                entry = self._get_reconfigure_entry()
                self.hass.config_entries.async_update_entry(entry, data=data)
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="Reconfigured!")

            return self.async_create_entry(
                title=str(user_input.get("identifier")), data=data
            )

        schema_dict = {}

        entry = None
        if self.source == config_entries.SOURCE_RECONFIGURE:
            entry = self._get_reconfigure_entry()
        defaults = entry.data if entry else {}

        vol_key = vol.Required(
            "identifier", description={"suggested_value": defaults.get("identifier")}
        )
        schema_dict[vol_key] = str

        for key, dev_class in SENSOR_KEYS.items():
            vol_key = vol.Optional(
                key, description={"suggested_value": defaults.get(key)}
            )

            schema_dict[vol_key] = selector.selector(
                {
                    "entity": {
                        "filter": {
                            "domain": (
                                "binary_sensor"
                                if (dev_class in {"plug", "lock"})
                                else "sensor"
                            ),
                            "device_class": dev_class,
                        }
                    }
                }
            )

        data_schema = vol.Schema(schema_dict)

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            description_placeholders={},
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, vol.Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Run reconfiguration of the integration."""
        _LOGGER.debug("Executing async_step_reconfigure...")
        return await self.async_step_user(user_input)
