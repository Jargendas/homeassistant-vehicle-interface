"""Entry point for Energy Stats integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import async_setup_api
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the new integration config entry."""
    _LOGGER.debug("Executing async_setup_entry (__init__)...")

    async_setup_api(hass, entry)

    _LOGGER.debug("Vehicle Interface entry set up")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the config entry."""
    _LOGGER.debug("Executing async_unload_entry...")
    hass.data.pop(entry.entry_id, None)
    return True
