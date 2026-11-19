# Blueprint "Drooff fire+: Holz nachlegen / Add wood"

Once Home Assistant has started, the integration installs the blueprint to `config/blueprints/automation/drooff_fireplus_v2/wood_required_notification.yaml` and updates it with new versions as long as you have not changed the file. After an update, automations are reloaded so they use the new version.

## Setup

1. Open *Settings*, *Automations & scenes*, *Blueprints*.
2. Choose **Drooff fire+: Holz nachlegen / Add wood**.
3. Choose German, English or French as **Sprache** (*Language*). It selects the default texts (title, "Please add wood.", "Add wood now!"); own texts replace them.
4. Select the *operation status* sensor of the fire+ as **Betriebsstatus** (*Operation status*).
5. Optionally select the *recommended wood load* sensor as **Empfohlene Holzauflage** (*Recommended wood load*). The message then says how much wood to add, by default as the number of logs, e.g. "Bitte Holz nachlegen. (2 Holzscheite)" (see [Wood load](#wood-load)).
6. Open the collapsed section **Aktion bei Holz nachlegen** (*Action when wood is required*), fill in the channels and save.

By default only **wood urgently required** notifies, with the channels of **Aktion bei Holz nachlegen** (*Action when wood is required*). To be reminded at *wood required* already, switch on **Bei "Holz nachlegen" melden** (*Notify when wood is required*) in that section.

## Wood load

The fire+ recommends the wood load in kg. With **Holzauflage angeben als** (*Show wood load as*) the message shows it as

| Setting | Example |
|---|---|
| Logs (*Holzscheite*, default) | Please add wood. (2 logs) |
| kg | Please add wood. (1.4 kg) |
| Logs and kg | Please add wood. (2 logs, 1.4 kg) |

The number of logs is the amount in kg divided by **Gewicht je Holzscheit** (*Weight per log*), rounded, at least 1. A single log reads "one log". The default of 0.7 kg follows Drooff's technical information (e.g. 1.4 kg in 2 logs at nominal heat output). Weigh a few of your own logs for a better value.

## Language

Home Assistant can not translate blueprints, so the blueprint shows all languages at once: every label is German, with English and French below it in smaller print. Options name all three languages, e.g. "Holzscheite / Logs / Bûches". **Sprache** (*Language*) switches the default texts of the messages (German, English, French). In French the message reads e.g. "Veuillez recharger du bois. (2 bûches)". For other languages, enter your own **Titel** (*Title*) and **Nachricht** (*Message*).

## Channels

Every channel is optional, a single one is enough (e.g. Echo only or Pushover only), and each has its own **delay** (*Verzögerung*). It only fires if the fire+ still asks for wood after the delay, so nothing is sent once the wood has been added.

| Channel | Inputs | Action |
|---|---|---|
| Message (*Nachricht*) | actions, preset with a Home Assistant notification (`notify.persistent_notification`, on) and Pushover (`notify.pushover`, off) | as entered |
| Echo | devices of *Alexa Media Player* (HACS) with type announce or TTS; notify entities of *Alexa Devices* (e.g. `notify.kitchen_announce`); own announcement text | `notify.alexa_media`; `notify.send_message` |
| Other actions (*Weitere Aktionen*) | any actions, the variables `title` and `text` hold title and message | as entered |

### Message via Pushover (or mobile app, Telegram, …)

Pushover is already prepared in **Nachricht: Aktionen** (*Message: actions*), but switched off. Choose **Enable** in the three-dot menu of the *Pushover* action. Priority and sound are under data, preset with `priority: 0` and `sound: pushover` (urgent: `priority: 1`, `sound: siren`). Switch off or delete the Home Assistant notification if you do not want it. For the mobile app or Telegram add an action such as *notify.mobile_app_…* with message `{{ text }}` and title `{{ title }}`.

**Echo only:** switch off or delete both preset message actions and choose devices or notify entities under Echo.

The preset Pushover action for *wood urgently required* in YAML, switched on:
```yaml
- action: notify.pushover
  data:
    title: "{{ title }}"
    message: "{{ text }}"
    data:
      priority: 1
      sound: siren
```
Several recipients are several actions. An empty channel sends nothing.

## Wood urgently required

The section **Aktion bei Dringend Holz nachlegen** (*Action when wood is urgently required*) is expanded. It has the same channels and texts and is only used once **Eigene Aktionen bei "Dringend" verwenden** (*Use own actions when urgent*) is switched on. Until then, *wood urgently required* runs the actions for *wood required*, with their delays but the urgent default text.

When the status changes from *wood required* to *urgently required*, pending reminders for *wood required* are dropped and the urgent channels start with their own delays.

After wood was added, the fire+ often goes from *urgently required* to *wood required* for a moment and then to *regular*. This way back sends no reminder, and pending urgent reminders are dropped.

## Other warnings

The collapsed section **Weitere Warnungen** (*Other warnings*) adds two optional warnings. Each is only active once its sensor is selected:

- **Tür zu lange offen** (*Door open too long*): the binary sensor of the same name. The fire+ door is open for more than 5 minutes while the stove is hotter than 40 °C, like the warning of the web app (only recent devices). Default text "The stove door has been open too long!".
- **Fehlermeldung (Kaminzug)** (*Error message (chimney draught)*): the *error message* sensor. It warns at *Chimney draught too low* ("The chimney has too little draught!") and *No chimney draught* ("The chimney has no draught!"), other errors do not warn.

Both have their own message (empty = default text of the selected language). **Aktionen der Warnungen** (*Actions of the warnings*) selects whether they run the actions of *wood urgently required* (default; only when **Eigene Aktionen bei "Dringend" verwenden** is on, otherwise those of *wood required*) or of *wood required*. A warning is sent right away, the delays of the channels do not apply, and the message has no wood load. The automation runs in restart mode: a warning stops a wood reminder that is still waiting for its delay.

## Customising

You can change the installed file. The integration remembers which version it installed and does not touch a file that differs from it, neither at a restart nor with an update. To get the current version again, delete the file and restart Home Assistant. If you would rather keep receiving updates, save your copy under another name in the same folder.

The `source_url` of the blueprint points to the release of the installed version (e.g. `…/blob/v2.0.5/…`), not to `main`. *Re-import blueprint* in Home Assistant and tools like *Blueprints Updater* therefore fetch exactly the installed version and do not offer a newer state of the repository that belongs to another version of the integration. New versions of the blueprint come with updates of the integration.
