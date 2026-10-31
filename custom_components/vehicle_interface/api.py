"""API implementation of Vehicle Interface integration."""

import logging
from http import HTTPStatus

from aiohttp import web
from homeassistant.components.image import DATA_COMPONENT as IMAGE_DATA_COMPONENT
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.http import HomeAssistantView

from .const import CONF_DEVICE_TRACKER, CONF_VEHICLE_IMAGE, SENSOR_KEYS

_LOGGER = logging.getLogger(__name__)


def _get_identifier(entry: ConfigEntry) -> str:
    """Return the normalized vehicle identifier used in the API paths."""
    return str(entry.data.get("identifier")).lower().replace(" ", "_")


class VehicleInterfaceAPI(HomeAssistantView):
    """API handling class for Vehicle Interface integration."""

    requires_auth = True

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize API functionality for entry."""
        self.hass = hass
        self.entry = entry
        identifier = _get_identifier(entry)
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
            if tracker_state:
                lat = tracker_state.attributes.get("latitude")
                lon = tracker_state.attributes.get("longitude")
                if lat is not None:
                    states["latitude"] = float(lat)
                if lon is not None:
                    states["longitude"] = float(lon)

        if self.entry.data.get(CONF_VEHICLE_IMAGE):
            states["image"] = f"{self.url}/image"

        _LOGGER.debug("Returning data: %s", str(states))
        return web.json_response(states)


class VehicleInterfaceImageAPI(HomeAssistantView):
    """Serve the configured vehicle image."""

    requires_auth = True

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize image endpoint for entry."""
        self.hass = hass
        self.entry = entry
        identifier = _get_identifier(entry)
        self.url = f"/api/{identifier}/image"
        self.name = f"api:{identifier}:image"

    async def get(self, _request) -> web.Response:  # noqa: ANN001
        """Return the vehicle image as binary response."""
        entity_id = self.entry.data.get(CONF_VEHICLE_IMAGE)
        if not entity_id:
            return web.Response(status=HTTPStatus.NOT_FOUND)

        component = self.hass.data.get(IMAGE_DATA_COMPONENT)
        entity = component.get_entity(entity_id) if component else None
        if entity is None:
            return web.Response(status=HTTPStatus.NOT_FOUND)

        try:
            content = await entity.async_image()
        except HomeAssistantError:
            _LOGGER.exception("Could not fetch vehicle image from %s", entity_id)
            return web.Response(status=HTTPStatus.INTERNAL_SERVER_ERROR)
        if not content:
            return web.Response(status=HTTPStatus.NOT_FOUND)

        return web.Response(body=content, content_type=entity.content_type)


def async_setup_api(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up the API."""
    _LOGGER.debug("Executing async_setup_api...")
    hass.http.register_view(VehicleInterfaceAPI(hass, entry))
    hass.http.register_view(VehicleInterfaceImageAPI(hass, entry))
