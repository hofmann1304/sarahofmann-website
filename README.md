# sarahofmann.de — statische Website

Statische HTML/CSS/JS-Website für **sarahofmann.de**. Kein Framework, kein CMS.
Die Website wird wie `robutrace.de` direkt aus dem Branch `main` über GitHub
Pages veröffentlicht. Das Kontaktformular nutzt einen eigenen Form.taxi-Endpunkt.

## Projektstruktur

```text
index.html              Startseite
uebermich.html          Über mich
consulting.html         Consulting
dozententaetigkeit.html Dozententätigkeit
nachhilfe.html          Nachhilfe
kontakt.html            Kontaktformular über Form.taxi
danke.html              Erfolgsseite nach Formular-Versand
insights.html           Übersicht der Insights
insights/               Einzelne Beiträge
impressum.html          Impressum
datenschutz.html        Datenschutzerklärung
agb.html                Allgemeine Geschäftsbedingungen
widerruf.html           Widerrufsbelehrung
404.html                Eigene Fehlerseite
assets/                 Bilder und Schriftarten; die öffentliche CV-Fassung folgt nach der Aktualisierung
css/style.css           Design
js/main.js              Navigation und dynamisches Footer-Jahr
scripts/                Prüf- und CV-Buildskripte
CNAME                   GitHub-Pages-Domain `sarahofmann.de`
.nojekyll               Unveränderte statische Auslieferung
sitemap.xml, robots.txt Suchmaschinen-Metadaten
```

## Suchmaschinenoptimierung

Die Website verwendet ausschließlich die sauberen, endungslosen URLs als
interne Ziele, Canonical-URLs und Sitemap-Einträge. Indexierbar sind die
Startseite, Profil- und Leistungsseiten, Kontakt, Insights-Übersicht und fünf
Fachartikel. Fehler-, Bestätigungs-, CV-Wartungs- und Rechtstextseiten tragen
`noindex` und stehen nicht in der Sitemap.

Strukturierte Daten kennzeichnen:

- Website und freiberufliches Unternehmen auf der Startseite,
- Sara Hofmann als Person auf der Über-mich-Seite,
- die drei Angebote als Leistungen,
- Fachartikel mit Autorin, Veröffentlichungsdatum und Titelbild.

Nach Veröffentlichung muss `https://sarahofmann.de/sitemap.xml` in der Google
Search Console eingereicht und die Indexierung beobachtet werden. Die frühere
Domain `sara-hofmann.de` sollte serverseitig per permanentem 301-Redirect auf
die jeweils passende URL unter `sarahofmann.de` weiterleiten. Ein bloßer Link
oder eine JavaScript-Weiterleitung ersetzt diese Migration nicht.

## Lokal testen

Die Seite kann direkt über `index.html` geöffnet werden. Für realistische
Pfad- und Linktests empfiehlt sich ein lokaler Server:

```bash
python -m http.server 8080
```

Danach `http://localhost:8080` öffnen. Das Kontaktformular darf bei lokalen
Tests nicht abgesendet werden, weil es echte Daten an Form.taxi übertragen
würde.

## Veröffentlichung über GitHub Pages

1. Repository öffentlich halten oder einen GitHub-Tarif verwenden, der Pages
   für private Repositories unterstützt.
2. Unter **Settings → Pages** aus dem Branch `main` und dem Verzeichnis `/`
   veröffentlichen.
3. Als Custom Domain `sarahofmann.de` hinterlegen und HTTPS erzwingen.
4. Bei INWX nur die Web-DNS-Einträge anpassen:
   - Apex-Domain auf die vier aktuellen GitHub-Pages-IPv4-Adressen,
   - `www` als CNAME auf `hofmann1304.github.io`.
5. Vorhandene MX-, SPF-, DKIM- und DMARC-Einträge für E-Mail unverändert lassen.

GitHub Pages veröffentlicht jeden Push auf `main` automatisch. Die Datei
`CNAME` hält die Domain-Zuordnung im Repository fest.

## Kontaktformular

Das Formular sendet per POST an einen ausschließlich für `sarahofmann.de`
angelegten Form.taxi-Endpunkt. Es enthält:

- einen Honeypot gegen einfache Spam-Bots,
- eine eigene Betreffzeile,
- die feste Erfolgsseite `https://sarahofmann.de/danke.html`,
- den Hinweis, keine vertraulichen Zugangsdaten zu übermitteln.

Formularsendungen müssen regelmäßig geprüft und entsprechend der
Datenschutzerklärung gelöscht werden.

## Veröffentlichungscheckliste

- Arbeitsbaum und Linkprüfung fehlerfrei
- Repository und GitHub Pages auf `main` synchron
- Custom Domain für Apex und `www` erreichbar
- HTTPS-Zertifikat genehmigt und HTTPS erzwungen
- HTTP und `www` leiten auf `https://sarahofmann.de/` weiter
- Formular mit ausdrücklich freigegebenen Testdaten geprüft
- Impressum, Datenschutz, AGB und Widerruf fachanwaltlich prüfen lassen

## Design-Entscheidungen

- Überschriften: lokal ausgeliefertes `Cormorant Infant`
- Fließtext und UI: lokal ausgeliefertes `Archivo`
- Keine Analyse-, Marketing- oder Trackingdienste
- Keine extern geladenen Webfonts
- Sprachhinweis im Header derzeit rein informativ; gepflegt wird Deutsch
