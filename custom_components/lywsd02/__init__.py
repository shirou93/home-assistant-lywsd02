from __future__ import annotations

import logging
import struct
import time
from datetime import datetime

from bleak.exc import BleakError
from bleak_retry_connector import (
    BleakClientWithServiceCache,
    close_stale_connections,
    establish_connection,
)

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

DOMAIN = "lywsd02"
CONF_MAC = "mac"
_LOGGER = logging.getLogger(__name__)

_UUID_TIME = "EBE0CCB7-7A0A-4B0C-8A1A-6FF2997DA3A6"
_UUID_TEMO = "EBE0CCBE-7A0A-4B0C-8A1A-6FF2997DA3A6"


def get_localized_timestamp() -> int:
    """Return a timestamp adjusted for the local timezone."""
    now = int(time.time())
    offset = datetime.now().astimezone().utcoffset()
    return now + int(offset.total_seconds())


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the LYWSD02 time update service."""

    hass.data.setdefault(DOMAIN, {})

    async def set_time(call: ServiceCall) -> None:
        mac = call.data.get(CONF_MAC, "").upper()
        if not mac:
            configured_macs = [
                entry_data[CONF_MAC]
                for entry_data in hass.data[DOMAIN].values()
                if CONF_MAC in entry_data
            ]
            if len(configured_macs) == 1:
                mac = configured_macs[0]

        if not mac:
            _LOGGER.error(
                "Missing 'mac' parameter. Configure a LYWSD02 integration entry "
                "or provide the address in the service call."
            )
            return

        tz_offset = call.data.get("tz_offset", 0)

        ble_device = bluetooth.async_ble_device_from_address(
            hass,
            mac,
            connectable=True,
        )

        if not ble_device:
            _LOGGER.error("Could not find BLE device with address '%s'.", mac)
            return

        _LOGGER.info("Found '%s' - attempting to update time...", ble_device)

        # Prepare settings
        temp_mode = (call.data.get("temp_mode") or "").upper()
        clock_mode = call.data.get("clock_mode", 0)
        tout = int(call.data.get("timeout", 60))

        data_temp_mode = data_clock_mode = None

        if temp_mode in ("C", "F"):
            data_temp_mode = struct.pack("B", 0x01 if temp_mode == "F" else 0xFF)
            _LOGGER.debug("Temperature mode set: %s", temp_mode)

        if clock_mode in (12, 24):
            data_clock_mode = struct.pack(
                "IHB", 0, 0, 0xAA if clock_mode == 12 else 0x00
            )
            _LOGGER.debug("Clock mode set: %s", clock_mode)

        client = None
        try:
            # Close any stale BLE connections for this device
            await close_stale_connections(ble_device)

            # Establish a reliable BLE connection with retries
            client = await establish_connection(
                BleakClientWithServiceCache,
                ble_device,
                name=f"LYWSD02_{mac}",
                timeout=tout,
                max_attempts=5,
            )

            timestamp = int(call.data.get("timestamp") or get_localized_timestamp())
            data_time = struct.pack("Ib", timestamp, tz_offset)

            await client.write_gatt_char(_UUID_TIME, data_time)

            if data_temp_mode is not None:
                await client.write_gatt_char(_UUID_TEMO, data_temp_mode)

            if data_clock_mode is not None:
                try:
                    await client.write_gatt_char(_UUID_TIME, data_clock_mode)
                except BleakError as err:
                    _LOGGER.warning(
                        "clock_mode (12/24-hour) could not be set on '%s': "
                        "it is only supported on the LYWSD02MMC and this "
                        "device rejected the write (%s). The time was set "
                        "successfully; remove the 'clock_mode' parameter to "
                        "silence this warning.",
                        mac,
                        err,
                    )

            _LOGGER.info(
                "Successfully updated time on '%s' to '%s' with offset '%s' hours.",
                mac,
                timestamp,
                tz_offset,
            )

        except Exception:
            _LOGGER.exception("Error while updating '%s'.", mac)
        finally:
            try:
                if client and client.is_connected:
                    await client.disconnect()
                    _LOGGER.debug("Disconnected from '%s'.", mac)
            except Exception:
                pass

    hass.services.async_register(DOMAIN, "set_time", set_time)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a LYWSD02 device configured through the UI."""

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry.data
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a LYWSD02 device configured through the UI."""

    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
