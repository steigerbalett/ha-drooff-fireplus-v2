# Changelog

## 2.0.1

- Dashboard card 1.0.8: larger flame animation. The flames are taller and wider, and the stove takes more room in the card (side by side up to 300 px wide instead of 250 px, stacked 300 px high instead of 240 px).

## 2.0.0

First version of **Drooff fire+ V2**, an independent continuation of [ha-drooff-fireplus](https://github.com/tehlers/ha-drooff-fireplus) by Thorsten Ehlers (@tehlers), version 1.5.0.

### Breaking changes

- New domain `drooff_fireplus_v2`, so V2 is a separate integration that has to be set up again. See *Switching from the original integration* in the README for how to keep entity IDs and history.
- The operation status reports lower-case, translated states (`regular`, `wood_required`, …) instead of `REGULAR`, `WOOD_REQUIRED`, …. Automations, scripts and templates that compare the state have to be adapted.
- Rarely needed diagnostic entities are disabled by default on new installations: operating time, Wifi signal strength, Ethernet link, web app version, automatic updates, online support.

### New

- Own icon, shown in Home Assistant and HACS (`brand/icon.png` in the integration).
- Dashboard card `custom:drooff-fireplus-card` (registered automatically): animated fire that follows the combustion state, values and controls, optional picture of your own stove, stove model list with the draught values of Drooff, draught gauge, temperature history, burn timeline, wood usage, alarm area (errors, draught warning, door open too long, filter problems), eight languages.
- Blueprint *Drooff fire+: Holz nachlegen / Add wood*, installed and updated with the integration: separate actions for wood required and wood urgently required, messages via any notify action, Echo announcements, other actions, each with its own delay, German and English.
- Statistics from the event log of the fire+: fires, reloads, estimated wood consumption, last reload; stored across restarts.
- Discovery via DHCP (default hostname `fire`), a changed IP address is picked up automatically.
- Sensors: control (web, panel, remote control, room controller), door open too long, particle filter status and problem (Blue Angel stoves), last update and update search, web app version, online support, automatic updates, draught warning.
- Diagnostics download without host and serial number.
- Tests for all platforms, the card and the blueprint; lint, test and release workflows.

### Fixed

- Settings are refused like in the web app while a remote control, room controller or the panel controls the fire+.
- Stoves with the Blue Angel label only offer Eco and Power.
- Burn rate with "Betrieb 1" is read like in the web app.
- Settings written at the same time no longer undo each other.
- Availability, cached configuration, failed writes are reported, a reconfiguration reloads the entry only once.
- Dashboard card on iOS Safari no longer scrolls back to the fire.
