# Drooff fire+ V2 for Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/docs/faq/custom_repositories/)
[![Release](https://img.shields.io/github/v/release/steigerbalett/ha-drooff-fireplus-v2)](https://github.com/steigerbalett/ha-drooff-fireplus-v2/releases)
[![Downloads](https://img.shields.io/github/downloads/steigerbalett/ha-drooff-fireplus-v2/total?label=downloads)](https://github.com/steigerbalett/ha-drooff-fireplus-v2/releases)
[![Downloads of the latest release](https://img.shields.io/github/downloads/steigerbalett/ha-drooff-fireplus-v2/latest/total?label=downloads%40latest)](https://github.com/steigerbalett/ha-drooff-fireplus-v2/releases/latest)
[![Validate](https://github.com/steigerbalett/ha-drooff-fireplus-v2/actions/workflows/validate.yml/badge.svg)](https://github.com/steigerbalett/ha-drooff-fireplus-v2/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/github/license/steigerbalett/ha-drooff-fireplus-v2)](LICENSE)

**English** | [Deutsch](README.de.md)

A custom integration for [Home Assistant](https://www.home-assistant.io/) for the [Drooff fire+](https://www.drooff-kaminofen.de/en/nature/electronic-combustion-control-fire/) combustion control system, with its own dashboard card, a wood reminder blueprint and statistics of every fire.

![Dashboard card](docs/images/overview.png)

## Origin and thanks

The idea and the foundation of this integration come from **Thorsten Ehlers ([@tehlers](https://github.com/tehlers))** and his [ha-drooff-fireplus](https://github.com/tehlers/ha-drooff-fireplus). He worked out how the fire+ web application talks to the stove, built the integration and maintained it with the help of its contributors. Without all this preparatory work, this fork and version 2 would not exist. Thank you very much!

Drooff fire+ V2 continues this work as an independent project, because the extensions became too large for the original repository. Please report problems with V2 [here](https://github.com/steigerbalett/ha-drooff-fireplus-v2/issues), not to the original project.

### Thanks to Drooff

A big thank you to **DROOFF Kaminöfen GmbH & Co. KG** for kindly allowing this project to use the Drooff logo and the product pictures of the stoves. This makes the integration look right at home in Home Assistant and in the dashboard card.

## What is new in version 2

- **Dashboard card** with an animated fire, controls, optional picture of your own stove, draught gauge, history graphics and an alarm area that only appears when something is wrong
- **Blueprint "Add wood"** with messages (Pushover, Telegram, mobile app, …), Echo announcements and any other actions, each with its own delay
- **Statistics** from the event log of the fire+: fires, reloads, estimated wood consumption, last reload
- **Control locks** like the web app (remote control, room controller, panel), Blue Angel stoves with Eco and Power only
- New sensors: door open too long, particle filter (Blue Angel), control, update status, web app settings
- Discovery via DHCP, translated operation states, diagnostics download, tests for all functions

The full list of changes is in the [changelog](CHANGELOG.md).

## Installation

### HACS

1. Ensure that [HACS](https://hacs.xyz) is installed.
2. In HACS, open the menu (three dots), choose *Custom repositories* and add `https://github.com/steigerbalett/ha-drooff-fireplus-v2` with the type *Integration*.
3. Search for "Drooff fire+ V2" in HACS and download it.
4. Restart Home Assistant.

[![Open your Home Assistant instance and open this repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=steigerbalett&repository=ha-drooff-fireplus-v2&category=integration)

### Manual installation

1. Download `drooff_fireplus_v2.zip` from the [latest release](https://github.com/steigerbalett/ha-drooff-fireplus-v2/releases/latest).
2. Unpack it into `custom_components/drooff_fireplus_v2` in the `config` directory of your Home Assistant.
3. Restart Home Assistant.

### Switching from the original integration

V2 has its own domain `drooff_fireplus_v2`. It can be installed next to the original integration *Drooff fire+* (`drooff_fireplus`), but both would then poll the same fire+. To switch:

1. Under *Settings*, *Devices & services*, delete the original integration *Drooff fire+*. Do this **first**, so the new entities get the same entity IDs as before.
2. In HACS, remove the original repository *Drooff fire+*.
3. Install V2 as described above, restart Home Assistant and set it up (see *Configuration*).

What carries over: Home Assistant keeps history and long-term statistics by entity ID, so with the same entity IDs your graphs continue. Dashboards and automations that use these entity IDs keep working. Check the entity IDs after the setup; an ID ending in `_2` means that an old entity still existed.

What does not carry over: settings changed in the options of the integration (polling interval, IPv4), entities you enabled, disabled or renamed by hand, and the device ID used by device triggers. Statistics of the integration (fires, reloads, wood) start again from the events the fire+ still has stored.

**Breaking change:** the operation status now has lower-case states (`wood_required` instead of `WOOD_REQUIRED`, …). Adapt your own automations, scripts and templates. Automations created from the blueprint of the original integration should be created again from the V2 blueprint *Drooff fire+: Holz nachlegen / Add wood*.

## Configuration

1. Go to *Settings* > *Devices & services* > *Add integration*.
2. Search for "Drooff fire+ V2" and select it.
3. Enter the hostname of your Drooff fire+ web application. In the default configuration, this is "fire".

If the fire+ keeps its default hostname "fire", Home Assistant usually discovers it automatically (DHCP) and offers to set it up under *Devices & services*. When the fire+ was set up with its IP address, a changed IP address is picked up automatically.

Diagnostics (parsed values and the raw responses of the fire+, host and serial number removed) can be downloaded on the device page for bug reports.

## Entities

### Controls

| Name             | Type   | Description                                              |
| ---------------- | ------ | -------------------------------------------------------- |
| `Burn rate`      | Number | Select burn rate in six stages between "Eco" and "Power" (only "Eco" and "Power" for stoves with the Blue Angel label) |
| `Ember burndown` | Switch | Toggle between "Ember preservation" and "Ember burndown" |
| `LED`            | Switch | Toggle LED (only Drooff fire+ v1)                        |

Like the fire+ web application, the integration refuses changes while the fire+ is not controlled via web: with a remote control all settings are locked, with a room controller or when the panel on the stove is selected the burn rate is locked. See `Control` below.

### Sensors

| Name                      | Type   | Description                                                   |
| ------------------------- | ------ | ------------------------------------------------------------- |
| `Air slider position`     | Sensor | Position of the air slider in percent                         |
| `Draught`                 | Sensor | Chimney draught in Pa                                         |
| `Heating progress`        | Sensor | Heating progress in percent (only available while `HEATING`)  |
| `Operation status`        | Sensor | Operation status of the fireplace, shown in the language of Home Assistant. The states (for automations) are:<br>- `standby`<br>- `regular`<br>- `heating`<br>- `wood_required`<br>- `wood_urgently_required`<br>- `ember_preservation`<br>- `ember_burndown`<br>- `error`<br>- `unknown`<br><br>Up to version 1.5 the states were upper-case (`REGULAR`, …). Automations and scripts that compare them have to be changed to the lower-case states. |
| `Temperature`             | Sensor | Temperature inside the combustion chamber in °C               |
| `Target temperature`      | Sensor | Target Temperature inside the combustion chamber in °C        |
| `Recommended wood load`   | Sensor | Recommended amount of wood to add in kg (only recent devices) |
| `Door`                    | Sensor | Door contact switch indicator                                 |
| `Door open too long`      | Binary Sensor | Problem when the door is open for more than 5 minutes while the temperature is above 40 °C, like the warning of the web app (only recent devices) |
| `Filter status`           | Sensor | Status of the OekoSolve particle filter: `driver_error`, `not_found`, `present`, `inactive`, `active`, `cleaning_required` or `error` (only stoves with the Blue Angel label) |
| `Filter problem`          | Binary Sensor | Problem when the web app shows the filter status in red: driver error, filter not found, cleaning required or another error (only stoves with the Blue Angel label) |

### Statistics

The integration reads the event log of the fire+ (door openings and phases, `php/easevents.php`) once a minute and keeps the counters across restarts. They are `total_increasing`, so the statistics graph card or a utility meter shows them per day, week or month.

| Name                           | Type   | Description |
| ------------------------------ | ------ | ----------- |
| `Fires`                        | Sensor | Fires: heating up followed by regular operation (heating up that ends in standby is not counted) |
| `Reloads`                      | Sensor | Door openings during regular operation; openings within 10 minutes count once |
| `Wood consumption (estimated)` | Sensor | Recommended wood load at every fire and reload, in kg. An estimate, the fire+ does not weigh the wood; while it recommends no load (for example in standby), the last known one is used (only recent devices) |
| `Last reload`                  | Sensor | Time of the last reload |

On the first start the counters include the events still stored on the fire+ (usually the last days). If the fire+ recommends no wood load at that time, the wood of these events is added as soon as it does. Older firmware without event log leaves these sensors unavailable.

### Configuration

| Name         | Type   | Description                                                     |
| ------------ | ------ | --------------------------------------------------------------- |
| `Brightness` | Number | Brightness of the LED strip in percent                          |
| `Volume`     | Number | Volume of the acoustic signal in percent (only Drooff fire+ v2) |

### Diagnostic

Entities that are rarely needed or that write many values to the database are disabled by default. Enable them on the device page under *Diagnostic*.

| Name                   | Type          | Description                                                       |
| ---------------------- | ------------- | ----------------------------------------------------------------- |
| `Error`                | Binary Sensor | Active when an error has been detected                            |
| `Error message`        | Sensor        | Description of the detected error. Possible values are:<br>- "No error"<br>- "Temperature sensor defective"<br>- "Pressure measurement defective"<br>- "Air slider defective"<br>- "Service mode enabled"<br>- "Chimney draught too low"<br>- "Air slider stuck"<br>- "No chimney draught"<br>- "Wrong motor direction"<br>- "Unknown error"<br><br>**Always consult the official fire+ web application in the event of an error!** |
| `Operating time`       | Sensor        | Total operating time of the fireplace in s (only Drooff fire+ v2). Disabled by default |
| `Wifi signal strength` | Sensor        | Strength of the Wifi signal (only Drooff fire+ v2). Disabled by default |
| `Ethernet link`        | Binary Sensor | Network is connected via Ethernet (only Drooff fire+ v2). Disabled by default |
| `Control`              | Sensor        | Who controls the fire+: `web`, `panel`, `remote_control`, `remote_control_automatic` or `room_controller` (only Drooff fire+ v2) |
| `Online support`       | Binary Sensor | Remote access for Drooff support is enabled (recent web applications). Disabled by default |
| `Automatic updates`    | Binary Sensor | The fire+ installs updates automatically (recent web applications). Disabled by default |
| `Draught warning`      | Binary Sensor | The draught warning of the fire+ is enabled (recent web applications) |
| `Web app version`      | Sensor        | Version of the fire+ web application (recent web applications). Disabled by default |
| `Last update`          | Sensor        | Result of the last software update: `no_updates`, `started`, `running`, `successful`, `failed`, `postponed` (until the stove is off), `not_started` or `unknown`. The message of the fire+ (German) is an attribute. Disabled by default, read once a minute while enabled |
| `Update search`        | Sensor        | When the fire+ looks for updates every week, e.g. "Mittwoch, 03:43 Uhr". Disabled by default |

## Dashboard card

The integration ships a Lovelace card with an animated fire that follows the current combustion state, next to the values and controls of the fire+. The card is registered automatically, no resource has to be added. Edit a dashboard, choose *Add card* and pick **Drooff fire+ Card**, or use YAML:

```yaml
type: custom:drooff-fireplus-card
```

The card editor detects the fire+ device and its entities automatically. Every value can be hidden, a picture of your own stove can be used, and optional graphics (temperature history, timeline, wood usage, draught gauge) can be enabled. All options are described in the [card documentation](docs/dashboard-card.md) ([Deutsch](docs/dashboard-card.de.md)).

## Blueprint: wood reminder

The integration installs the automation blueprint **Drooff fire+: Holz nachlegen / Add wood** to `blueprints/automation/drooff_fireplus_v2/` once Home Assistant has started, and updates it with new versions of the integration as long as you have not changed the file. Go to *Settings*, *Automations & scenes*, *Blueprints* and create an automation from it.

It reminds you when the fire+ asks for wood. *Wood required* and *wood urgently required* get separate actions, the urgent ones are optional and hidden in their own section. Each kind of reminder can be sent as a message (Pushover, Telegram, mobile app or any other notify action or entity), as an announcement on Amazon Echo devices (Alexa Media Player or Alexa Devices) and as any other actions. Every channel is optional and has its own delay, and nothing is sent once the wood has been added. Details are in the [blueprint documentation](docs/blueprint.md) ([Deutsch](docs/blueprint.de.md)).

The blueprint is labelled in German and English, its default texts follow the selected language (German or English). If you change the installed file, your changes are kept and the integration no longer updates it. Delete the file to get the current version again at the next start.

## Credits

- [Thorsten Ehlers (@tehlers)](https://github.com/tehlers): original integration [ha-drooff-fireplus](https://github.com/tehlers/ha-drooff-fireplus), on which this version is built
- All contributors of the original project
- Based on the [integration blueprint](https://github.com/ludeeus/integration_blueprint) by @ludeeus
- [DROOFF Kaminöfen GmbH & Co. KG](https://www.drooff-kaminofen.de/): logo and product pictures, used with kind permission

## Logo and pictures

The Drooff logo (`custom_components/drooff_fireplus_v2/brand/`) and the product pictures of the stoves are the property of

DROOFF Kaminöfen GmbH & Co. KG
Keffelker Str. 40
D-59929 Brilon

They are used with the kind permission of Drooff. They are **not** covered by the MIT license of this project and must not be changed or used in any other way. Details are in [NOTICE.md](NOTICE.md).

## Disclaimer

> [!IMPORTANT]
> This integration is neither supported nor affiliated with Drooff. It is intended as a supplement to the official fire+ webapp and not a full replacement.
