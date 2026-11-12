# Drooff fire+ V2 für Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/docs/faq/custom_repositories/)
[![Release](https://img.shields.io/github/v/release/steigerbalett/ha-drooff-fireplus-v2)](https://github.com/steigerbalett/ha-drooff-fireplus-v2/releases)
[![Downloads](https://img.shields.io/github/downloads/steigerbalett/ha-drooff-fireplus-v2/total?label=downloads)](https://github.com/steigerbalett/ha-drooff-fireplus-v2/releases)
[![Downloads der aktuellen Version](https://img.shields.io/github/downloads/steigerbalett/ha-drooff-fireplus-v2/latest/total?label=downloads%40latest)](https://github.com/steigerbalett/ha-drooff-fireplus-v2/releases/latest)
[![Validate](https://github.com/steigerbalett/ha-drooff-fireplus-v2/actions/workflows/validate.yml/badge.svg)](https://github.com/steigerbalett/ha-drooff-fireplus-v2/actions/workflows/validate.yml)
[![Lizenz: MIT](https://img.shields.io/github/license/steigerbalett/ha-drooff-fireplus-v2)](LICENSE)

[English](README.md) | **Deutsch**

Eine benutzerdefinierte Integration für [Home Assistant](https://www.home-assistant.io/) für die Abbrandsteuerung [Drooff fire+](https://www.drooff-kaminofen.de/). Dazu gehören eine eigene Dashboard-Karte, ein Blueprint zum Holznachlegen und eine Statistik über jeden Abbrand.

![Dashboard-Karte](docs/images/overview-de.png)

## Ursprung und Dank

Die Idee und das Fundament dieser Integration stammen von **Thorsten Ehlers ([@tehlers](https://github.com/tehlers))** und seiner Integration [ha-drooff-fireplus](https://github.com/tehlers/ha-drooff-fireplus). Er hat herausgefunden, wie die Webapp des fire+ mit dem Ofen spricht, die Integration aufgebaut und sie zusammen mit ihren Mitwirkenden gepflegt. Erst all diese Vorarbeit hat diesen Fork und diese Version 2 möglich gemacht. Vielen Dank dafür!

Drooff fire+ V2 führt diese Arbeit als eigenständiges Projekt fort, weil die Erweiterungen für das ursprüngliche Repository zu umfangreich geworden sind. Probleme mit V2 bitte [hier melden](https://github.com/steigerbalett/ha-drooff-fireplus-v2/issues), nicht beim ursprünglichen Projekt.

### Dank an Drooff

Ein großes Dankeschön an die **DROOFF Kaminöfen GmbH & Co. KG**, die diesem Projekt freundlicherweise erlaubt, das Drooff-Logo und die Produktbilder der Öfen zu verwenden. So fügt sich die Integration in Home Assistant und in der Dashboard-Karte wie selbstverständlich ein.

## Neu in Version 2

- **Dashboard-Karte** mit animiertem Feuer, Bedienung, Bild deines Ofens (81 Produktbilder von Drooff dabei), Zeigerinstrument für den Kaminzug, Verlaufsgrafiken und einer Alarmanzeige, die nur erscheint, wenn etwas nicht stimmt
- **Blueprint „Holz nachlegen“** mit Nachrichten (Pushover, Telegram, Companion-App, …), Echo-Ansagen und beliebigen weiteren Aktionen, jeweils mit eigener Verzögerung
- **Statistik** aus dem Ereignis-Log des fire+: Abbrände, Nachlegevorgänge, geschätzter Holzverbrauch, zuletzt nachgelegt
- **Bediensperren** wie in der Webapp (Fernbedienung, Raumregler, Panel), bei Öfen mit Blauem Engel nur Eco und Power
- Neue Sensoren: Tür zu lange offen, Feinstaubfilter (Blauer Engel), Bedienung, Update-Status, Einstellungen der Webapp
- Erkennung per DHCP, übersetzter Betriebsstatus, Diagnose-Download, Tests für alle Funktionen

Alle Änderungen stehen im [Changelog](CHANGELOG.md) (englisch).

## Installation

### HACS

1. [HACS](https://hacs.xyz) muss installiert sein.
2. In HACS das Menü (drei Punkte) öffnen, *Benutzerdefinierte Repositories* wählen und `https://github.com/steigerbalett/ha-drooff-fireplus-v2` mit dem Typ *Integration* hinzufügen.
3. In HACS nach „Drooff fire+ V2“ suchen und herunterladen.
4. Home Assistant neu starten.

[![Öffne deine Home-Assistant-Instanz und zeige dieses Repository im Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=steigerbalett&repository=ha-drooff-fireplus-v2&category=integration)

### Manuelle Installation

1. `drooff_fireplus_v2.zip` aus dem [aktuellen Release](https://github.com/steigerbalett/ha-drooff-fireplus-v2/releases/latest) herunterladen.
2. In den Ordner `custom_components/drooff_fireplus_v2` im `config`-Verzeichnis von Home Assistant entpacken.
3. Home Assistant neu starten.

### Umstieg von der ursprünglichen Integration

V2 hat eine eigene Domain `drooff_fireplus_v2`. Sie lässt sich neben der ursprünglichen Integration *Drooff fire+* (`drooff_fireplus`) installieren, dann fragen aber beide denselben fire+ ab. Zum Umstieg:

1. Unter *Einstellungen*, *Geräte & Dienste* die ursprüngliche Integration *Drooff fire+* löschen. Das **zuerst** tun, damit die neuen Entitäten dieselben Entitäts-IDs wie bisher bekommen.
2. In HACS das ursprüngliche Repository *Drooff fire+* entfernen.
3. V2 wie oben beschrieben installieren, Home Assistant neu starten und einrichten (siehe *Einrichtung*).

Was erhalten bleibt: Home Assistant speichert Verlauf und Langzeitstatistik nach Entitäts-ID. Mit denselben Entitäts-IDs laufen die Diagramme also weiter, und Dashboards und Automationen mit diesen Entitäts-IDs funktionieren weiter. Nach der Einrichtung die Entitäts-IDs prüfen: Endet eine auf `_2`, gab es die alte Entität noch.

Was nicht erhalten bleibt: in den Optionen geänderte Einstellungen (Abfrageintervall, IPv4), von Hand aktivierte, deaktivierte oder umbenannte Entitäten und die Geräte-ID, die Geräte-Auslöser verwenden. Die Statistik der Integration (Abbrände, Nachlegen, Holz) beginnt neu, mit den Ereignissen, die der fire+ noch gespeichert hat.

**Breaking Change:** Der Betriebsstatus hat jetzt kleingeschriebene Werte (`wood_required` statt `WOOD_REQUIRED`, …). Eigene Automationen, Skripte und Templates müssen angepasst werden. Automationen aus dem Blueprint der ursprünglichen Integration am besten neu aus dem V2-Blueprint *Drooff fire+: Holz nachlegen / Add wood* anlegen.

## Einrichtung

1. *Einstellungen* > *Geräte & Dienste* > *Integration hinzufügen* öffnen.
2. Nach „Drooff fire+ V2“ suchen und auswählen.
3. Den Hostnamen der fire+ Webapp eingeben. In der Standardeinstellung ist das „fire“.

Behält der fire+ seinen Standard-Hostnamen „fire“, findet Home Assistant ihn meist automatisch (DHCP) und bietet unter *Geräte & Dienste* die Einrichtung an. Wurde der fire+ mit seiner IP-Adresse eingerichtet, wird eine geänderte IP-Adresse automatisch übernommen.

Die Diagnose (ausgewertete Werte und die Rohantworten des fire+, ohne Host und Seriennummer) lässt sich für Fehlerberichte auf der Geräteseite herunterladen.

## Entitäten

### Bedienung

| Name | Typ | Beschreibung |
| --- | --- | --- |
| `Brennleistung` | Zahl | Brennleistung in sechs Stufen zwischen „Eco“ und „Power“ (bei Öfen mit Blauem Engel nur „Eco“ und „Power“) |
| `Glutabbrand` | Schalter | Umschalten zwischen „Gluterhaltung“ und „Glutabbrand“ |
| `LED` | Schalter | LED ein- und ausschalten (nur Drooff fire+ v1) |

Wie die fire+ Webapp lehnt die Integration Änderungen ab, solange der fire+ nicht über das Web bedient wird. Mit Fernbedienung sind alle Einstellungen gesperrt, mit Raumregler oder bei Bedienung am Panel des Ofens die Brennleistung. Siehe `Bedienung` unten.

### Sensoren

| Name | Typ | Beschreibung |
| --- | --- | --- |
| `Luftschieberposition` | Sensor | Stellung des Luftschiebers in Prozent |
| `Feinzug` | Sensor | Kaminzug in Pa |
| `Anheizfortschritt` | Sensor | Fortschritt des Anheizens in Prozent (nur beim Anheizen verfügbar) |
| `Betriebsstatus` | Sensor | Betriebszustand des Ofens, angezeigt in der Sprache von Home Assistant. Die Werte (für Automationen) sind:<br>- `standby`<br>- `regular`<br>- `heating`<br>- `wood_required`<br>- `wood_urgently_required`<br>- `ember_preservation`<br>- `ember_burndown`<br>- `error`<br>- `unknown`<br><br>Bis Version 1.5 waren die Werte großgeschrieben (`REGULAR`, …). Automationen und Skripte, die sie vergleichen, müssen auf die kleingeschriebenen Werte umgestellt werden. |
| `Temperatur` | Sensor | Temperatur im Brennraum in °C |
| `Zieltemperatur` | Sensor | Zieltemperatur im Brennraum in °C |
| `Empfohlene Holzauflage` | Sensor | Empfohlene Holzmenge zum Nachlegen in kg (nur neuere Geräte) |
| `Tür` | Binärsensor | Türkontakt |
| `Tür zu lange offen` | Binärsensor | Problem, wenn die Tür länger als 5 Minuten offen ist und die Temperatur über 40 °C liegt, wie die Warnung der Webapp (nur neuere Geräte) |
| `Filterstatus` | Sensor | Status des ÖkoSolve-Feinstaubfilters: `driver_error`, `not_found`, `present`, `inactive`, `active`, `cleaning_required` oder `error` (nur Öfen mit Blauem Engel) |
| `Filterproblem` | Binärsensor | Problem, wenn die Webapp den Filterstatus rot anzeigt: Treiberfehler, Filter nicht gefunden, reinigen oder ein anderer Fehler (nur Öfen mit Blauem Engel) |

### Statistik

Die Integration liest einmal pro Minute das Ereignis-Log des fire+ (Türöffnungen und Phasen, `php/easevents.php`) und behält die Zähler über Neustarts hinweg. Sie sind `total_increasing`, die Statistik-Karte oder ein Verbrauchszähler zeigen sie also pro Tag, Woche oder Monat.

| Name | Typ | Beschreibung |
| --- | --- | --- |
| `Abbrände` | Sensor | Abbrände: Anheizen, auf das Regelbetrieb folgt (Anheizen, das in Standby endet, zählt nicht) |
| `Nachlegevorgänge` | Sensor | Türöffnungen im Regelbetrieb; Öffnungen innerhalb von 10 Minuten zählen einmal |
| `Holzverbrauch (geschätzt)` | Sensor | Empfohlene Holzauflage bei jedem Abbrand und Nachlegen, in kg. Eine Schätzung, der fire+ wiegt das Holz nicht; empfiehlt er gerade keine Auflage (z. B. in Standby), wird die letzte bekannte genutzt (nur neuere Geräte) |
| `Zuletzt nachgelegt` | Sensor | Zeitpunkt des letzten Nachlegens |

Beim ersten Start enthalten die Zähler die Ereignisse, die noch auf dem fire+ gespeichert sind (meist die letzten Tage). Empfiehlt der fire+ zu diesem Zeitpunkt keine Holzauflage, wird das Holz dieser Ereignisse nachgetragen, sobald er es tut. Ältere Firmware ohne Ereignis-Log lässt diese Sensoren nicht verfügbar.

### Konfiguration

| Name | Typ | Beschreibung |
| --- | --- | --- |
| `Helligkeit` | Zahl | Helligkeit des LED-Streifens in Prozent |
| `Lautstärke` | Zahl | Lautstärke des Signaltons in Prozent (nur Drooff fire+ v2) |

### Diagnose

Selten gebrauchte Entitäten und solche, die viele Werte in die Datenbank schreiben, sind standardmäßig deaktiviert. Aktivieren lassen sie sich auf der Geräteseite unter *Diagnose*.

| Name | Typ | Beschreibung |
| --- | --- | --- |
| `Fehler` | Binärsensor | Aktiv, wenn ein Fehler erkannt wurde |
| `Fehlermeldung` | Sensor | Beschreibung des erkannten Fehlers. Mögliche Werte:<br>- „Kein Fehler“<br>- „Temperatursensor defekt“<br>- „Druckmessung defekt“<br>- „Luftschieber defekt“<br>- „Servicemodus aktiviert“<br>- „Kaminzug zu niedrig“<br>- „Luftschieber klemmt“<br>- „Kein Kaminzug“<br>- „Motor dreht in die falsche Richtung“<br>- „Unbekannter Fehler“<br><br>**Im Fehlerfall immer die offizielle fire+ Webapp zu Rate ziehen!** |
| `Betriebszeit` | Sensor | Gesamtbetriebszeit des Ofens in s (nur Drooff fire+ v2). Standardmäßig deaktiviert |
| `WLAN Signalstärke` | Sensor | Stärke des WLAN-Signals (nur Drooff fire+ v2). Standardmäßig deaktiviert |
| `Ethernet-Verbindung` | Binärsensor | Netzwerk ist per Ethernet verbunden (nur Drooff fire+ v2). Standardmäßig deaktiviert |
| `Bedienung` | Sensor | Wer den fire+ bedient: `web`, `panel`, `remote_control`, `remote_control_automatic` oder `room_controller` (nur Drooff fire+ v2) |
| `Online-Support` | Binärsensor | Fernzugriff für den Drooff-Support ist eingeschaltet (neuere Webapps). Standardmäßig deaktiviert |
| `Automatische Updates` | Binärsensor | Der fire+ installiert Updates automatisch (neuere Webapps). Standardmäßig deaktiviert |
| `Zugwarnung` | Binärsensor | Die Zugwarnung des fire+ ist eingeschaltet (neuere Webapps) |
| `Version Webapp` | Sensor | Version der fire+ Webapp (neuere Webapps). Standardmäßig deaktiviert |
| `Letztes Update` | Sensor | Ergebnis des letzten Software-Updates: `no_updates`, `started`, `running`, `successful`, `failed`, `postponed` (bis der Ofen aus ist), `not_started` oder `unknown`. Die Meldung des fire+ ist ein Attribut. Standardmäßig deaktiviert, wird nur bei Aktivierung einmal pro Minute gelesen |
| `Update-Suche` | Sensor | Wann der fire+ wöchentlich nach Updates sucht, z. B. „Mittwoch, 03:43 Uhr“. Standardmäßig deaktiviert |

## Dashboard-Karte

Die Integration bringt eine Lovelace-Karte mit. Sie zeigt ein animiertes Feuer, das dem aktuellen Abbrandzustand folgt, neben den Werten und der Bedienung des fire+. Die Karte wird automatisch registriert, eine Ressource muss nicht angelegt werden. Dashboard bearbeiten, *Karte hinzufügen* wählen und **Drooff fire+ Card** auswählen, oder per YAML:

```yaml
type: custom:drooff-fireplus-card
```

Der Karteneditor findet das fire+ Gerät und seine Entitäten automatisch. Jeder Wert lässt sich ausblenden, ein Bild des eigenen Ofens lässt sich verwenden, und optionale Grafiken (Temperaturverlauf, Zeitleiste, Holzverbrauch, Zeigerinstrument für den Zug) lassen sich einschalten. Alle Optionen beschreibt die [Kartendokumentation](docs/dashboard-card.de.md) ([English](docs/dashboard-card.md)).

## Blueprint: Holz nachlegen

Die Integration installiert den Automations-Blueprint **Drooff fire+: Holz nachlegen / Add wood** nach dem Start von Home Assistant in `blueprints/automation/drooff_fireplus_v2/` und aktualisiert ihn mit neuen Versionen der Integration, solange du die Datei nicht geändert hast. Unter *Einstellungen*, *Automationen & Szenen*, *Blueprints* lässt sich daraus eine Automation anlegen.

Er erinnert, wenn der fire+ nach Holz verlangt. *Holz nachlegen* und *Dringend Holz nachlegen* bekommen eigene Aktionen, die dringenden sind optional und stecken in einem eigenen Abschnitt. Jede Art der Erinnerung kann als Nachricht (Pushover, Telegram, Companion-App oder jede andere Notify-Aktion oder -Entität), als Ansage auf Amazon-Echo-Geräten (Alexa Media Player oder Alexa Devices) und als beliebige andere Aktionen gesendet werden. Jeder Kanal ist optional und hat eine eigene Verzögerung, und sobald Holz nachgelegt wurde, wird nichts mehr gesendet. Details stehen in der [Blueprint-Dokumentation](docs/blueprint.de.md) ([English](docs/blueprint.md)).

Der Blueprint ist deutsch und englisch beschriftet, seine Standardtexte folgen der gewählten Sprache. Änderst du die installierte Datei, bleiben deine Änderungen erhalten und die Integration aktualisiert sie nicht mehr. Wer die Datei löscht, bekommt beim nächsten Start wieder die aktuelle Version.

## Mitwirkende und Dank

- [Thorsten Ehlers (@tehlers)](https://github.com/tehlers): ursprüngliche Integration [ha-drooff-fireplus](https://github.com/tehlers/ha-drooff-fireplus), auf der diese Version aufbaut
- Alle Mitwirkenden des ursprünglichen Projekts
- Grundlage ist der [Integration Blueprint](https://github.com/ludeeus/integration_blueprint) von @ludeeus
- [DROOFF Kaminöfen GmbH & Co. KG](https://www.drooff-kaminofen.de/): Logo und Produktbilder, mit freundlicher Genehmigung

## Logo und Bilder

Das Drooff-Logo (`custom_components/drooff_fireplus_v2/brand/`) und die Produktbilder der Öfen sind Eigentum der

DROOFF Kaminöfen GmbH & Co. KG
Keffelker Str. 40
D-59929 Brilon

Sie werden mit freundlicher Genehmigung von Drooff verwendet. Sie fallen **nicht** unter die MIT-Lizenz dieses Projekts. Die Produktbilder werden mit der Integration ausgeliefert (`custom_components/drooff_fireplus_v2/frontend/stoves/`) und dürfen nur in ihr verwendet werden; die Karte darf sie für die Anzeige freistellen. Darüber hinaus dürfen sie nicht verändert oder anderweitig genutzt werden. Details stehen in [NOTICE.md](NOTICE.md) und in der [Lizenz der Bilder](custom_components/drooff_fireplus_v2/frontend/stoves/LICENSE.md).

## Haftungsausschluss

> [!IMPORTANT]
> Diese Integration wird von Drooff weder unterstützt noch steht sie mit Drooff in Verbindung. Sie ist als Ergänzung zur offiziellen fire+ Webapp gedacht und kein vollständiger Ersatz.
