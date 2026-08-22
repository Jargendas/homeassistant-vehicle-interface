"""API implementation of Vehicle Interface integration."""

import logging

from aiohttp import web
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.http import HomeAssistantView

from .const import CONF_DEVICE_TRACKER, SENSOR_KEYS

_LOGGER = logging.getLogger(__name__)


class VehicleInterfaceAPI(HomeAssistantView):
    """API handling class for Vehicle Interface integration."""

    requires_auth = True

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize API functionality for entry."""
        self.hass = hass
        self.entry = entry
        identifier = str(entry.data.get("identifier")).lower().replace(" ", "_")
        self.url = f"/api/{identifier}"
        self.name = f"api:{identifier}"
        _LOGGER.debug("Vehicle Interface API initialized as %s", self.url)

    async def get(self, _request) -> web.Response:  # noqa: ANN001
        """Handle the API get requests."""
        sensors_ids = {k: self.entry.data.get(k) for k in SENSOR_KEYS}
        _LOGGER.debug("Handling GET request for sensors: %s", str(sensors_ids.values()))

        def get_value(entity_id: str) -> str | float | bool | None:  # noqa: PLR0911
            if not entity_id:
                return None
            st = self.hass.states.get(entity_id)
            _LOGGER.debug("Fetched state for %s: %s", entity_id, st)
            if not st or st.state in ("unknown", "unavailable", None):
                return None
            try:
                if st.attributes.get("device_class") == "timestamp":
                    return str(st.state)
                return float(st.state)
            except (ValueError, TypeError):
                if st.state == "on":
                    return True
                if st.state == "off":
                    return False
                return None

        states = {k: get_value(v) for k, v in sensors_ids.items() if v}

        # If a device_tracker is configured, extract lat/lon from it (takes priority)
        tracker_id = self.entry.data.get(CONF_DEVICE_TRACKER)
        if tracker_id:
            tracker_state = self.hass.states.get(tracker_id)
            if tracker_state and tracker_state.state not in ("unknown", "unavailable", None):
                lat = tracker_state.attributes.get("latitude")
                lon = tracker_state.attributes.get("longitude")
                if lat is not None:
                    states["latitude"] = float(lat)
                if lon is not None:
                    states["longitude"] = float(lon)

        _LOGGER.debug("Returning data: %s", str(states))
        return web.json_response(states)


def async_setup_api(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up the API."""
    _LOGGER.debug("Executing async_setup_api...")
    hass.http.register_view(VehicleInterfaceAPI(hass, entry))
