# Blueprint "Drooff fire+: Holz nachlegen / Add wood"

Once Home Assistant has started, the integration installs the blueprint to `config/blueprints/automation/drooff_fireplus_v2/wood_required_notification.yaml` and updates it with new versions as long as you have not changed the file. After an update, automations are reloaded so they use the new version.

## Setup

1. Open *Settings*, *Automations & scenes*, *Blueprints*.
2. Choose **Drooff fire+: Holz nachlegen / Add wood**.
3. Choose German or English as **Sprache / Language**. It selects the default texts (title, "Please add wood.", "Add wood now!"); own texts replace them.
4. Select the *operation status* sensor of the fire+ as **Betriebsstatus / Operation status**.
5. Optionally select the *recommended wood load* sensor as **Empfohlene Holzauflage / Recommended wood load**. The message then says how much wood to add, by default as the number of logs, e.g. "Bitte Holz nachlegen. (2 Holzscheite)" (see [Wood load](#wood-load)).
6. Fill in the channels in the section **Aktion bei Holz nachlegen / Action when wood is required** and save.

## Wood load

The fire+ recommends the wood load in kg. With **Holzauflage angeben als / Show wood load as** the message shows it as

| Setting | Example |
|---|---|
| Logs (*Holzscheite*, default) | Please add wood. (2 logs) |
| kg | Please add wood. (1.4 kg) |
| Logs and kg | Please add wood. (2 logs, 1.4 kg) |

The number of logs is the amount in kg divided by **Gewicht je Holzscheit / Weight per log**, rounded, at least 1. The default of 0.7 kg follows Drooff's technical information (e.g. 1.4 kg in 2 logs at nominal heat output). Weigh a few of your own logs for a better value.

## Language

The labels of the blueprint are bilingual (German / English), because Home Assistant can not translate blueprints. **Sprache / Language** switches the default texts of the messages.

## Channels

Every channel is optional, a single one is enough (e.g. Echo only or Pushover only), and each has its own **delay** (*Verzögerung*). It only fires if the fire+ still asks for wood after the delay, so nothing is sent once the wood has been added.

| Channel | Inputs | Action |
|---|---|---|
| Message (*Nachricht*) | actions, preset with a Home Assistant notification (`notify.persistent_notification`, on) and Pushover (`notify.pushover`, off) | as entered |
| Echo | devices of *Alexa Media Player* (HACS) with type announce or TTS; notify entities of *Alexa Devices* (e.g. `notify.kitchen_announce`); own announcement text | `notify.alexa_media`; `notify.send_message` |
| Other actions (*Weitere Aktionen*) | any actions, the variables `title` and `text` hold title and message | as entered |

### Message via Pushover (or mobile app, Telegram, …)

Pushover is already prepared in **Message: actions**, but switched off. Choose **Enable** in the three-dot menu of the *Pushover* action. Priority and sound are under data, preset with `priority: 0` and `sound: pushover` (urgent: `priority: 1`, `sound: siren`). Switch off or delete the Home Assistant notification if you do not want it. For the mobile app or Telegram add an action such as *notify.mobile_app_…* with message `{{ text }}` and title `{{ title }}`.

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

The section **Aktion bei Dringend Holz nachlegen / Action when wood is urgently required** is collapsed. It has the same channels and texts and is only used once **Use own actions when urgent** is switched on. Until then, *wood urgently required* runs the actions for *wood required*, with their delays but the urgent default text.

When the status changes from *wood required* to *urgently required*, pending reminders for *wood required* are dropped and the urgent channels start with their own delays.

## Customising

You can change the installed file. The integration remembers which version it installed and does not touch a file that differs from it, neither at a restart nor with an update. To get the current version again, delete the file and restart Home Assistant. If you would rather keep receiving updates, save your copy under another name in the same folder.
