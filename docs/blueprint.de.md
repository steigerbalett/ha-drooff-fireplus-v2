# Blueprint „Drooff fire+: Holz nachlegen / Add wood“

Die Integration installiert den Blueprint nach dem Start von Home Assistant nach `config/blueprints/automation/drooff_fireplus_v2/wood_required_notification.yaml` und aktualisiert ihn mit neuen Versionen, solange du die Datei nicht geändert hast. Ist eine Automation mit einer älteren Version des Blueprints aktiv, lädt die Integration die Automationen danach neu.

## Einrichten

1. *Einstellungen*, *Automationen & Szenen*, *Blueprints* öffnen.
2. **Drooff fire+: Holz nachlegen / Add wood** wählen.
3. Bei **Sprache** Deutsch oder Englisch wählen. Die Sprache bestimmt die Standardtexte (Titel, „Bitte Holz nachlegen.“, „Dringend Holz nachlegen!“). Eigene Texte ersetzen sie.
4. Bei **Betriebsstatus** den Sensor „Betriebsstatus“ des fire+ eintragen.
5. Optional bei **Empfohlene Holzauflage** den gleichnamigen Sensor eintragen. Dann wird die Menge in kg an die Nachricht angehängt, zum Beispiel „Bitte Holz nachlegen. (1.5 kg)“.
6. Im Bereich **Aktion bei Holz nachlegen** die gewünschten Kanäle ausfüllen und speichern.

## Sprache

Die Beschriftungen im Blueprint sind zweisprachig (Deutsch / Englisch), weil Home Assistant Blueprints nicht übersetzen kann. Die Auswahl **Sprache** schaltet die Standardtexte der Nachrichten um.

## Kanäle

Jeder Kanal ist optional, ein einziger reicht, z. B. nur Echo oder nur Pushover. Leere Kanäle tun nichts. Jeder Kanal hat eine eigene **Verzögerung**. Er meldet sich erst, wenn der fire+ so lange ununterbrochen „Holz nachlegen“ anzeigt. Wird vorher nachgelegt, kommt nichts.

| Kanal | Eingaben | Aufruf |
|---|---|---|
| Nachricht | Aktionen, vorbelegt mit einer Benachrichtigung in Home Assistant (`notify.persistent_notification`, eingeschaltet) und Pushover (`notify.pushover`, ausgeschaltet) | wie eingetragen |
| Echo | Geräte von *Alexa Media Player* (HACS) mit Art „Ansage“ oder „TTS“; Notify-Entitäten von *Alexa Devices* (z. B. `notify.kueche_announce`); eigener Ansagetext | `notify.alexa_media`; `notify.send_message` |
| Weitere Aktionen | Beliebige Aktionen, die Variablen `title` und `text` enthalten Titel und Nachricht | wie eingetragen |

### Nachricht per Pushover (oder Handy-App, Telegram, …)

Pushover ist unter **Nachricht: Aktionen** schon vorbereitet, aber ausgeschaltet:

1. Bei der Aktion *Pushover* über das Drei-Punkte-Menü **Aktivieren** wählen.
2. Unter **Daten** stehen Priorität und Ton, vorbelegt mit `priority: 0` und `sound: pushover`, bei „Dringend“ mit `priority: 1` und `sound: siren`. Weitere Pushover-Felder wie `url` oder `ttl` lassen sich dort ergänzen.
3. Soll keine Benachrichtigung in Home Assistant erscheinen, diese Aktion ausschalten oder löschen.

Für die Handy-App oder Telegram eine Aktion hinzufügen, z. B. *notify.mobile_app_…*, mit **Nachricht** `{{ text }}` und **Titel** `{{ title }}`.

**Nur Echo:** beide vorbelegten Nachrichten-Aktionen ausschalten oder löschen und unter Echo Geräte oder Notify-Entitäten wählen.

Die vorbereitete Pushover-Aktion für „Dringend“ sieht eingeschaltet in YAML so aus:
```yaml
- action: notify.pushover
  data:
    title: "{{ title }}"
    message: "{{ text }}"
    data:
      priority: 1
      sound: siren
```
Mehrere Empfänger sind einfach mehrere Aktionen. Ein leerer Kanal (alle Aktionen gelöscht) sendet nichts.

## Dringend Holz nachlegen

Der Bereich **Aktion bei Dringend Holz nachlegen** ist zugeklappt. Er hat dieselben Kanäle und Texte wie „Holz nachlegen“ und gilt erst, wenn dort **Eigene Aktionen bei „Dringend“ verwenden / Use own actions when urgent** eingeschaltet ist. Solange der Schalter aus ist, löst auch „Dringend Holz nachlegen“ die Aktionen für „Holz nachlegen“ aus, mit deren Verzögerung, aber mit dem Standardtext für „Dringend“.

Wechselt der Status von „Holz nachlegen“ zu „Dringend“, werden noch ausstehende Erinnerungen für „Holz nachlegen“ verworfen und die Kanäle für „Dringend“ starten mit ihren eigenen Verzögerungen.

## Anpassen

Die installierte Datei darf geändert werden. Die Integration merkt sich, welche Version sie installiert hat, und lässt eine davon abweichende Datei in Ruhe, beim Neustart wie beim Update. Um wieder die aktuelle Version zu bekommen, die Datei löschen und Home Assistant neu starten. Wer weiter Updates bekommen möchte, speichert seine Anpassung im selben Ordner unter einem anderen Namen.
