# Blueprint „Drooff fire+: Holz nachlegen / Add wood“

Die Integration installiert den Blueprint nach dem Start von Home Assistant nach `config/blueprints/automation/drooff_fireplus_v2/wood_required_notification.yaml` und aktualisiert ihn mit neuen Versionen, solange du die Datei nicht geändert hast. Ist eine Automation mit einer älteren Version des Blueprints aktiv, lädt die Integration die Automationen danach neu.

## Einrichten

1. *Einstellungen*, *Automationen & Szenen*, *Blueprints* öffnen.
2. **Drooff fire+: Holz nachlegen / Add wood** wählen.
3. Bei **Sprache** Deutsch, Englisch oder Französisch wählen. Die Sprache bestimmt die Standardtexte (Titel, „Bitte Holz nachlegen.“, „Dringend Holz nachlegen!“). Eigene Texte ersetzen sie.
4. Bei **Betriebsstatus** den Sensor „Betriebsstatus“ des fire+ eintragen.
5. Optional bei **Empfohlene Holzauflage** den gleichnamigen Sensor eintragen. Dann steht in der Nachricht, wie viel Holz nachgelegt werden soll, standardmäßig als Anzahl der Holzscheite, zum Beispiel „Bitte Holz nachlegen. (2 Holzscheite)“ (siehe [Holzauflage](#holzauflage)).
6. Den zugeklappten Bereich **Aktion bei Holz nachlegen** öffnen, die gewünschten Kanäle ausfüllen und speichern.

Standardmäßig meldet sich nur **Dringend Holz nachlegen**, mit den Kanälen aus **Aktion bei Holz nachlegen**. Wer schon bei „Holz nachlegen“ erinnert werden möchte, schaltet dort **Bei „Holz nachlegen“ melden** ein.

## Holzauflage

Der fire+ empfiehlt die Holzauflage in kg. Mit **Holzauflage angeben als** zeigt die Nachricht sie als

| Einstellung | Beispiel |
|---|---|
| Holzscheite (Standard) | Bitte Holz nachlegen. (2 Holzscheite) |
| kg | Bitte Holz nachlegen. (1.4 kg) |
| Holzscheite und kg | Bitte Holz nachlegen. (2 Holzscheite, 1.4 kg) |

Die Anzahl der Holzscheite ist die Menge in kg geteilt durch das **Gewicht je Holzscheit**, gerundet und mindestens 1. Bei einem Scheit heißt es „Ein Holzscheit“. Der Standardwert 0,7 kg folgt den technischen Informationen von Drooff (z. B. 1,4 kg in 2 Holzscheiten bei Nennwärmeleistung). Genauer wird es, wenn du ein paar eigene Scheite wiegst.

## Sprache

Home Assistant kann Blueprints nicht übersetzen, deshalb zeigt der Blueprint alle Sprachen auf einmal: Jede Beschriftung ist deutsch, darunter stehen Englisch und Französisch in kleinerer Schrift. Auswahlfelder nennen alle drei Sprachen, z. B. „Holzscheite / Logs / Bûches“. Die Auswahl **Sprache** schaltet die Standardtexte der Nachrichten um (Deutsch, Englisch, Französisch). Für Französisch heißt die Nachricht z. B. „Veuillez recharger du bois. (2 bûches)“. Weitere Sprachen gehen über eigene Texte bei **Titel** und **Nachricht**.

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

Der Bereich **Aktion bei Dringend Holz nachlegen** ist aufgeklappt. Er hat dieselben Kanäle und Texte wie „Holz nachlegen“ und gilt erst, wenn dort **Eigene Aktionen bei „Dringend“ verwenden** eingeschaltet ist. Solange der Schalter aus ist, löst auch „Dringend Holz nachlegen“ die Aktionen für „Holz nachlegen“ aus, mit deren Verzögerung, aber mit dem Standardtext für „Dringend“.

Wechselt der Status von „Holz nachlegen“ zu „Dringend“, werden noch ausstehende Erinnerungen für „Holz nachlegen“ verworfen und die Kanäle für „Dringend“ starten mit ihren eigenen Verzögerungen.

Nach dem Nachlegen geht der fire+ von „Dringend“ oft erst kurz auf „Holz nachlegen“ und dann auf „Regelbetrieb“. Dieser Rückweg löst keine Erinnerung aus, und noch ausstehende Erinnerungen für „Dringend“ werden verworfen.

## Weitere Warnungen

Der zugeklappte Bereich **Weitere Warnungen** enthält zwei optionale Warnungen. Jede ist erst aktiv, wenn ihr Sensor eingetragen ist:

- **Tür zu lange offen**: der gleichnamige Binärsensor. Die Tür der fire+ ist länger als 5 Minuten offen, während der Ofen über 40 °C heiß ist, wie die Warnung der Webapp (nur neuere Geräte). Standardtext „Die Ofentür ist zu lange offen!“.
- **Fehlermeldung (Kaminzug)**: der Sensor „Fehlermeldung“. Er warnt bei „Kaminzug zu gering“ („Der Schornstein hat zu wenig Zug!“) und „Kein Kaminzug“ („Der Schornstein hat keinen Zug!“), andere Fehler lösen keine Warnung aus.

Beide haben eine eigene Nachricht (leer = Standardtext der gewählten Sprache). **Aktionen der Warnungen** legt fest, ob sie die Aktionen von „Dringend Holz nachlegen“ (Standard; nur wenn **Eigene Aktionen bei „Dringend“ verwenden** an ist, sonst die von „Holz nachlegen“) oder von „Holz nachlegen“ auslösen. Eine Warnung geht sofort raus, die Verzögerungen der Kanäle gelten nicht, und die Nachricht enthält keine Holzauflage. Die Automation läuft im Modus „restart“: Eine Warnung beendet eine Holz-Erinnerung, die noch auf ihre Verzögerung wartet.

## Anpassen

Die installierte Datei darf geändert werden. Die Integration merkt sich, welche Version sie installiert hat, und lässt eine davon abweichende Datei in Ruhe, beim Neustart wie beim Update. Um wieder die aktuelle Version zu bekommen, die Datei löschen und Home Assistant neu starten. Wer weiter Updates bekommen möchte, speichert seine Anpassung im selben Ordner unter einem anderen Namen.

Die `source_url` des Blueprints zeigt auf das Release der installierten Version (z. B. `…/blob/v2.0.5/…`), nicht auf `main`. „Blueprint erneut importieren“ in Home Assistant und Werkzeuge wie *Blueprints Updater* holen deshalb genau die installierte Version und bieten keinen neueren Stand des Repositorys an, der zu einer anderen Version der Integration gehört. Neue Versionen des Blueprints kommen mit den Updates der Integration.
