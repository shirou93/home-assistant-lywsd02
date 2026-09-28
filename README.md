# Home Assistant - LYWSD02 Sync Clock

Synchronize Xiaomi LYWSD02 e-ink clocks through Home Assistant Bluetooth. Bluetooth proxies, including ESPHome proxies, are supported.

## Latest Changelog

### 0.4.1

- Fixed local-time conversion that could set the clock to the previous date.
- Improved BLE connection handling and declared the BLE retry dependency.
- Made unsupported `clock_mode` writes non-fatal; the time is still set.
- Omitted `temp_mode` no longer triggers a temperature-unit change.

## Installation

### HACS

[![HACS badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/)

1. In HACS, open **Integrations** and select **Custom repositories** from the menu.
2. Add `https://github.com/shirou93/home-assistant-lywsd02` and choose **Integration** as the category.
3. Install **LYWSD02 Sync Clock** and restart Home Assistant.

## Configuration

No YAML configuration is required. In Home Assistant, open **Settings > Devices & services > Add integration**, search for **LYWSD02 Sync Clock**, and complete setup. This adds the service; clocks are selected by MAC address when the service is called.

## Synchronize Time

Call `lywsd02.set_time` with the clock's Bluetooth MAC address:

```yaml
service: lywsd02.set_time
data:
  mac: A1:B2:C3:D4:E5:F6
```

When no `timestamp` is supplied, the service sets the current Home Assistant time. Add the service to an automation to synchronize the clock periodically.

## Service Parameters

```yaml
service: lywsd02.set_time
data:
  mac: A1:B2:C3:D4:E5:F6
  timeout: 60
  clock_mode: 24
  temp_mode: C
  tz_offset: 0
```

- `mac`: target clock's Bluetooth address; required.
- `timestamp`: optional UNIX timestamp to set instead of the current time.
- `timeout`: BLE connection timeout in seconds; defaults to `60`.
- `temp_mode`: optional `C` or `F` temperature unit. Omit it to leave the current setting unchanged.
- `clock_mode`: optional `12` or `24` hour format. Supported only on the LYWSD02MMC; the plain LYWSD02 rejects this setting, but the time is still set and a warning is logged.
- `tz_offset`: optional timezone offset in hours sent with the time command.

See the [service definition](custom_components/lywsd02/services.yaml) for the fields exposed in Home Assistant.
