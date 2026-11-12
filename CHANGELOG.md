# Changelog

## 2.0.4b2

Beta: HACS offers it once *Show beta versions* is switched on for the repository.

- Product pictures of Drooff for every fire+ stove (83 variants), with the kind permission of DROOFF Kaminöfen GmbH & Co. KG. They are not covered by the MIT license, see `pictures/stoves/LICENSE.md` and NOTICE.md.
- Dashboard card 1.0.11: after the stove model, the editor asks step by step for version (e.g. APRICA 2 Trend, BRUNELLO 2 L Groove), variant (steel, steel with cladding, cladding, StilBeton, ArtBeton) and colour. The colours are small previews with their name. Clicking one loads the picture from the GitHub repository of the integration (`pictures/stoves/`), cuts it out and uses the window measured for it. Only the previews (about 130 KB) are part of the integration, so the download stays small. Choosing a picture needs internet access once, afterwards it is stored in the card.
- Fire chamber of the card (wall *Fire-clay plates*): three plates like in the Drooff stoves, one on the back wall and one on each side wall, instead of seven smaller ones.
- New card option `stove_window_soft` lets the window fade into the glass of the picture. Pictures that are already transparent keep white parts of the stove.
- Draft release action: a version like `2.0.4b1` or `2.0.4rc1` becomes a pre-release, and the final version counts as higher than its betas.

## 2.0.3

- The official Drooff logo is the icon of the integration, and the product pictures may be used, with the kind permission of DROOFF Kaminöfen GmbH & Co. KG. Thanks to Drooff! Logo and pictures are not covered by the MIT license, see NOTICE.md.
- Blueprint: a copy you changed in `blueprints/automation/drooff_fireplus_v2/` is no longer overwritten. The integration stores the hash of the version it installed and only updates a file that still matches it (or one of the versions shipped before). Deleting the file installs the current version again.
- Dashboard card 1.0.9: texts from the `translations` option are escaped before they go into the card and the editor, so markup in them is shown as text.

## 2.0.2

- Blueprint *Holz nachlegen / Add wood*: Pushover is prepared in the message actions (switched off, priority and sound under data, siren for urgent). A single channel is enough, e.g. Echo only or Pushover only. Inputs the automation editor stores as empty values no longer stop the reminder.

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
