# Vehicle Interface

A custom Home Assistant integration that exposes your vehicle's sensor data through a single authenticated REST endpoint. Useful for external displays, smart mirrors, dashboards, or any system that needs a unified JSON snapshot of your vehicle's current state.

---

## Features

- Aggregates multiple vehicle-related Home Assistant entities into one JSON API response
- Authenticated endpoint (requires a long-lived access token)
- Supports optional Device Tracker as a location source (overrides individual latitude/longitude sensors)
- Works with HACS

---

## Requirements

- Home Assistant 2025.2.4 or newer
- HACS 2.0.5 or newer (for HACS installation)
- Vehicle data already available as Home Assistant entities (e.g. from a car integration)

---

## Installation

### Via HACS (recommended)

1. Open HACS in your Home Assistant instance.
2. Go to **Integrations** → click the three-dot menu → **Custom repositories**.
3. Add `https://github.com/Jargendas/homeassistant-vehicle-interface` as an **Integration**.
4. Search for **Vehicle Interface** and install it.
5. Restart Home Assistant.

### Manual

1. Copy the `custom_components/vehicle_interface` folder into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.

---

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **Vehicle Interface**.
3. Fill in the fields described below and click **Submit**.

To update the configuration later, open the integration entry and choose **Reconfigure**.

### Configuration Fields

| Field | Description |
|---|---|
| **Vehicle Identifier** | A unique name for your vehicle. Determines the API endpoint path (e.g. `my_car` → `/api/my_car`). |
| **Last Data Update Time** | Sensor entity with device class `timestamp` — when the vehicle data was last refreshed. |
| **Total Mileage** | Sensor entity (device class `distance`) for the total odometer reading. |
| **Doors Locked/Unlocked** | Binary sensor entity (device class `lock`) indicating door lock state. |
| **Fuel Range** | Sensor entity (device class `distance`) for remaining fuel range. |
| **Electric Range** | Sensor entity (device class `distance`) for remaining electric range. |
| **Electric State of Charge** | Sensor entity (device class `battery`) for the battery charge level. |
| **Charger Connected/Disconnected** | Binary sensor entity (device class `plug`) indicating whether a charger is connected. |
| **Air Conditioning On/Off** | Any binary sensor entity indicating whether the air conditioning is active. |
| **Location Latitude** | Sensor entity providing the vehicle's latitude (used if no Device Tracker is configured). |
| **Location Longitude** | Sensor entity providing the vehicle's longitude (used if no Device Tracker is configured). |
| **Device Tracker** | A `device_tracker` entity. When set, its `latitude` and `longitude` attributes override the individual location sensors above. |

All fields except **Vehicle Identifier** are optional.

---

## API Endpoint

Once configured, the integration registers an authenticated HTTP endpoint at:

```
GET /api/<identifier>
```

Where `<identifier>` is the vehicle identifier entered during setup, lowercased and with spaces replaced by underscores.

### Authentication

Include a [long-lived access token](https://developers.home-assistant.io/docs/auth_api/#long-lived-access-token) in the `Authorization` header:

```
Authorization: ******
```

### Example Response

```json
{
  "update_time": "2025-06-01T12:00:00+00:00",
  "mileage": 42350.0,
  "door_lock": true,
  "fuel_range": 320.0,
  "electric_range": 85.0,
  "state_of_charge": 72.0,
  "connector_status": false,
  "aircon": false,
  "latitude": 48.1374,
  "longitude": 11.5755
}
```

Only fields that are configured and have a valid state are included in the response. Fields that are `unknown`, `unavailable`, or not configured are omitted.

### Value Types

| JSON key | Type | Notes |
|---|---|---|
| `update_time` | `string` | ISO 8601 timestamp |
| `mileage` | `number` | Unit depends on source entity |
| `door_lock` | `boolean` | `true` = locked |
| `fuel_range` | `number` | Unit depends on source entity |
| `electric_range` | `number` | Unit depends on source entity |
| `state_of_charge` | `number` | Percentage |
| `connector_status` | `boolean` | `true` = connected |
| `aircon` | `boolean` | `true` = on |
| `latitude` | `number` | Decimal degrees |
| `longitude` | `number` | Decimal degrees |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the [MIT License](LICENSE).