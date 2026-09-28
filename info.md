# LYWSD02 Sync Clock

Add the integration in **Settings > Devices & services > Add integration** and select **LYWSD02 Sync Clock**. No YAML setup is required. The integration provides the `lywsd02.set_time` service; specify the clock's Bluetooth MAC address when calling it.

```yaml
service: lywsd02.set_time
data:
  mac: A1:B2:C3:D4:E5:F6
```

The service sets the current Home Assistant time by default. You can also pass `timestamp`, `timeout`, `temp_mode`, `clock_mode`, or `tz_offset`. The connection timeout defaults to 60 seconds. See the [README](README.md#service-parameters) for all parameters and the [latest changelog](README.md#latest-changelog).

`clock_mode` (`12` or `24`) is supported only on the LYWSD02MMC. On the plain LYWSD02, the clock rejects this optional setting; the time is still set and a warning is logged.
