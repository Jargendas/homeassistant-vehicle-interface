"""Constants for Energy Stats integration."""

DOMAIN = "vehicle_interface"

# Die Keys, die im ConfigFlow als auswählbare Sensoren auftauchen
SENSOR_KEYS = {
    "update_time": "timestamp",
    "mileage": "distance",
    "door_lock": "lock",
    "fuel_range": "distance",
    "electric_range": "distance",
    "state_of_charge": "battery",
    "connector_status": "plug",
    "latitude": "Location Latitude",
    "longitude": "Location Longitude",
}
