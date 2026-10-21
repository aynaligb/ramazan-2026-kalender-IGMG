# Ramazan · Berlin

Eine statische, responsive Kalenderseite für Ramazan 1447 / 2026. Mit allen 29
Imsak-/Iftar-Zeitpaaren, Tagesauswahl, Monatsfiltern, besonderen Tagen, Abo und
ICS-Download. Keine externen Schriften, Analysewerkzeuge oder Laufzeitbibliotheken.
Die vollständige Tabelle und Downloads funktionieren auch ohne JavaScript.

## Quelle und Datenstand

- [IGMG Berlin, Ramazan İmsakiyesi 2026](https://berlin-igmg.de/aktuell/)
- [Originalkalender als Bild](https://berlin-igmg.de/wp-content/uploads/2026/01/Berlin_igmg_imsakiye_2026-1086x1536.png)
- Visueller Abgleich am 21. Oktober 2026: alle 58 Fastenzeiten stimmen überein.
- Kadir Gecesi: 16. März, Arefe: 19. März, erster Bayram-Tag: 20. März.
- **07:24 Uhr für das Bayram-Gebet ist in dieser Quelle nicht belegt.** Die zwei
  bisherigen Einträge bleiben mit ihren IDs erhalten, tragen aber den ausdrücklichen
  Hinweis zur Bestätigung bei der örtlichen Moschee.
- Kadir Gecesi und Arefe sind als Tagesmarkierungen eingetragen; die bisherige
  unbelegte Uhrzeit 22:00 beziehungsweise 12:00 entfällt. Die Nacht beginnt am Abend.

Privates Kalenderprojekt, kein offizieller IGMG-Auftritt.

## Kalenderformat

63 eindeutige Termine. Der bisherige Dateiname und alle UIDs bleiben erhalten,
damit bestehende Abonnements weiter funktionieren. Die Datei verwendet UTF-8,
CRLF, auf maximal 75 Bytes gefaltete Zeilen und eine eingebettete Europe/Berlin-
Zeitzone. Die Änderungen haben `SEQUENCE:1`. Termine blockieren keine Verfügbarkeit.
Bayram ist ein ganztägiger Termin vom 20. bis einschließlich 22. März; `DTEND`
ist gemäß iCalendar exklusiv der 23. März. Imsak-Alarme sind relativ 30 Minuten
vorher, Iftar-Alarme zur Startzeit. Kalender-Apps können Alarme aus Abo-Kalendern
ignorieren oder individuell behandeln; nach Einrichtung überprüfen.

## Abonnieren oder importieren

Die dauerhafte, jahresunabhängige HTTPS-Adresse für neue Abonnements:

```text
https://raw.githubusercontent.com/aynaligb/ramazan-2026-kalender-IGMG/refs/heads/main/berlin-ramazan.ics
```

- **Apple:** [Kalenderabonnement hinzufügen](https://support.apple.com/de-de/102301).
- **Google/Android:** Im Browser auf einem Computer unter Weitere Kalender →
  + → Per URL hinzufügen. Anschließend in der App im selben Konto einblenden.
  [Google-Anleitung](https://support.google.com/calendar/answer/37100?hl=de).
- **Outlook im Web:** Kalender hinzufügen → Vom Web abonnieren.
  [Microsoft-Anleitung](https://support.microsoft.com/de-de/outlook/import-or-subscribe-to-a-calendar-in-outlook-com-or-outlook-on-the-web).

Das dauerhafte Abo übernimmt Korrekturen und neue Jahresausgaben, sobald diese
geprüft veröffentlicht werden. Die App bestimmt das Aktualisierungsintervall.
Die bisherige Adresse `Ramazan_2026_Berlin_IGMG.ics` bleibt als Jahresarchiv
erhalten und wird nicht auf ein anderes Jahr umgebogen. Bestehende Nutzer
wechseln einmalig zur neuen Abo-Adresse und entfernen das alte Abo, um doppelte
2026-Termine zu vermeiden. Beim neuen Abo bleibt der Kalendername „Ramazan · Berlin“
jahresunabhängig. Ein Import der heruntergeladenen Jahresdatei ist eine einmalige Kopie. Die Einrichtung in echten Apple-, Google- und Outlook-Kalendern
ist nicht Teil der automatisierten Prüfungen.

## Lokal ansehen und prüfen

Python 3.9+ mit Zeitzonendaten und Node.js für die Syntaxprüfung:

```sh
python3 scripts/build_calendar.py
python3 scripts/verify_calendar.py
node --check app.js
python3 -m http.server 8000 --bind 127.0.0.1
```

Danach `http://127.0.0.1:8000` öffnen. Die GitHub-Action prüft dieselben
Kalenderregeln und ob die generierten Dateien zum Datenstand passen.

## Korrekturen und kommende Jahre

`data/calendar.json` ist die gemeinsame Datenquelle für Kalender und Tabelle.
Für eine Korrektur Daten ändern, `updated` aktualisieren, neu generieren und prüfen.
Bei einer späteren inhaltlichen Änderung auch die Sequenznummer im Generator erhöhen.
Bestehende UIDs nicht neu vergeben.

Für ein weiteres Jahr zuerst einen offiziellen, stadtspezifischen Kalender
beschaffen und jede Zeit mit der Quelle abgleichen. Dann neue Jahresdaten mit
neuen UIDs ergänzen und die Jahresangaben, Sondertage, Datumsgrenzen in `app.js`
sowie die Ausgabe in `index.html` anpassen. Der Generator erzeugt den passenden
Jahresdateinamen und aktualisiert automatisch `berlin-ramazan.ics` auf dieselbe
freigegebene Ausgabe. Bestehende Jahresdateien bleiben unverändert verfügbar.
Die dauerhafte Adresse bleibt jedes Jahr gleich; sie liefert die jeweils neueste
freigegebene Ausgabe und ist kein Gesamtarchiv aller Jahre. Der Prüflauf stellt
sicher, dass beide Dateien dieselben Termine und IDs enthalten.
Es gibt keine automatische Ermittlung oder Fortschreibung ungeprüfter Gebetszeiten.
Die jährliche Übernahme der offiziellen Quelldaten bleibt ein redaktioneller Schritt;
die Bereitstellung hinter der dauerhaften Abo-Adresse geschieht beim Generieren.

## Veröffentlichung

Die Dateien im Repository-Hauptverzeichnis können direkt über GitHub Pages
aus dem Branch `main` veröffentlicht werden. Kein Build-System erforderlich.
Die eingebetteten Kalenderadressen verweisen absichtlich auf `main`, damit
Abonnements nicht an einen temporären Arbeitsbranch gebunden sind.
