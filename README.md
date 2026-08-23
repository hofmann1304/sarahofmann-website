# sarahofmann.de — statische Website

Statische HTML/CSS/JS-Website für **sarahofmann.de**. Kein Framework, kein CMS.
Das Kontaktformular nutzt Netlify Forms; deshalb ist Netlify der vorgesehene Hoster.

## Projektstruktur

```
index.html              Startseite (Insights-Vorschau, 2 neueste Artikel)
uebermich.html
consulting.html
dozententaetigkeit.html
nachhilfe.html
kontakt.html             Kontaktformular (Netlify Forms)
danke.html                Erfolgsseite nach Formular-Versand
insights.html             Alle Insights-Artikel (Übersicht)
impressum.html
datenschutz.html
agb.html
widerruf.html             Widerrufsbelehrung und Muster-Widerrufsformular
404.html                  Eigene Fehlerseite
insights/                 Die 5 einzelnen Blogartikel
assets/images/            Bilder (Logo, Portrait, Blog-Thumbnails, Favicons)
assets/cv/                 Öffentliche, datensparsame CV-Fassung
assets/fonts/              Lokal ausgelieferte Webfonts
css/style.css             Gesamtes Design
js/main.js                 Mobile-Navigation, Footer-Jahr
scripts/build_public_cv.py Reproduzierbarer CV-Build
sitemap.xml, robots.txt
```

## Lokal testen

Einfach `index.html` per Doppelklick im Browser öffnen — die Seite
funktioniert vollständig offline über `file://`.

Für ein realistischeres Testsetup (z. B. um das Kontaktformular-Verhalten
zu prüfen) kann alternativ ein einfacher lokaler Server gestartet werden:

```bash
# Python (meist vorinstalliert)
python -m http.server 8080

# oder mit Node
npx serve .
```

Anschließend `http://localhost:8080` im Browser öffnen.

**Hinweis zum Kontaktformular:** Netlify Forms funktioniert nur, wenn die
Seite tatsächlich über Netlify ausgeliefert wird (siehe unten). Lokal oder
bei anderen Hostern zeigt das Formular keine Fehlermeldung, sendet aber
auch keine echte Nachricht.

## Deploy auf Netlify

**Variante A — Drag & Drop (am schnellsten):**
1. Bei [app.netlify.com](https://app.netlify.com) einloggen.
2. Auf der Startseite den kompletten Projektordner per
   Drag & Drop in den Upload-Bereich ziehen.
3. Netlify erkennt das Kontaktformular (`<form name="contact" ...>`)
   automatisch beim Deploy und aktiviert Netlify Forms — keine weitere
   Konfiguration nötig.
4. Formular-Einsendungen erscheinen danach unter *Site → Forms* im
   Netlify-Dashboard; optional dort eine E-Mail-Benachrichtigung an
   `hofmann1304@gmail.com` einrichten (*Forms → Settings & usage →
   Form notifications*).

**Variante B — Git-Verknüpfung (empfohlen für laufende Updates):**
1. Projekt in ein GitHub-Repository pushen.
2. In Netlify: *Add new site → Import an existing project* → Repository
   auswählen.
3. Build-Einstellungen: **kein Build-Command nötig**, *Publish directory*
   auf `/` (Projekt-Root) setzen.
4. Jeder Push auf den Hauptbranch deployt automatisch neu.

### Eigene Domain (sarahofmann.de) verbinden

Unter *Site settings → Domain management → Add a domain* die Domain
`sarahofmann.de` hinzufügen, als primäre Domain festlegen und Netlifys aktuell
angezeigten Anweisungen für die DNS-Einträge beim Domainanbieter INWX folgen.
`www.sarahofmann.de` wird auf die primäre Domain umgeleitet.

**Wichtig:** DNS-Werte nicht aus älteren Anleitungen übernehmen, sondern die im
konkreten Netlify-Projekt angezeigten Werte verwenden. Beim Umstellen nur die für
Website und `www` erforderlichen A-/ALIAS-/CNAME-Einträge ändern. Vorhandene
MX-Einträge für E-Mail bleiben unangetastet.

Nach erfolgreicher DNS-Zuordnung stellt Netlify das TLS-Zertifikat automatisch
bereit. Danach müssen HTTP-zu-HTTPS-Weiterleitung, Zertifikat für Hauptdomain und
`www`, Formularversand sowie E-Mail-Benachrichtigung praktisch getestet werden.

## Veröffentlichungscheckliste

- Netlify-Projekt mit dem GitHub-Repository verbinden; kein Build-Command, Publish-Verzeichnis `/`.
- Formularerkennung aktivieren und eine Benachrichtigung für neue Einsendungen einrichten.
- Einen echten Testeintrag senden, Eingang prüfen und den Testeintrag danach löschen.
- Formularübermittlungen regelmäßig prüfen und nach der in der Datenschutzerklärung festgelegten Frist löschen.
- `sarahofmann.de` als primäre Domain festlegen und `www` auf die Hauptdomain umleiten.
- Automatisches HTTPS abwarten und anschließend Zertifikat, Weiterleitungen und Sicherheitsheader prüfen.
- Impressum, Datenschutz, AGB und Widerruf vor dem endgültigen Start fachanwaltlich prüfen lassen.

## Design-Entscheidungen

- **Überschriften-Schrift:** `Cormorant Infant` — lokal unter `assets/fonts/`
  gespeichert und ohne Verbindung zu Google ausgeliefert.
- **Fließtext/UI-Schrift:** Das Original nutzt die kostenpflichtige
  Adobe-Schrift *Aktiv Grotesk Extended* (Typekit). Da diese nicht frei
  lizenzierbar ist, wurde sie durch **`Archivo`** ersetzt — eine freie
  Google-Font mit ähnlichem, breitem Grotesk-Charakter. Beide Schriften
  werden lokal von dieser Website ausgeliefert.
- **Farben:** Navy `#253551` (Akzentfarbe, Buttons, CV-Badge), Creme
  `#E0E0DB` (Info-Karten auf den Service-Seiten), Weiß/Schwarz für
  Hintergrund und Text — 1:1 aus der Live-Seite ausgelesen.
- **Bilder:** Alle Original-Bilder (Logo, Portraitfoto, 5
  Blog-Vorschaubilder) wurden heruntergeladen und für die Web-Auslieferung
  als komprimiertes JPEG (Fotos) bzw. optimiertes PNG (Logo, wegen
  Transparenz) neu gespeichert.
- **Kontaktformular:** Läuft über **Netlify Forms** inkl. Honeypot-Feld
  (`bot-field`) gegen Spam-Bots, mit eigener Erfolgsseite (`danke.html`).
- **Sprachumschalter:** Im Header vorhanden (wie im Original), aber rein
  dekorativ/informativ — die Seite wird aktuell ausschließlich auf
  Deutsch gepflegt, daher niedrige Priorität laut Briefing.
- **Mitglieder-/Buchungsbereich:** Auf der Live-Seite nicht vorhanden,
  daher entfällt dieser Punkt im Nachbau.

## Bekannte Abweichungen vom Original

- Die Original-URLs verwenden teils andere Pfade (z. B.
  `/dozententtigkeit` ohne "ä", `/insights/<slug>`). Der Nachbau nutzt
  stattdessen saubere, sprechende Dateinamen (z. B.
  `dozententaetigkeit.html`, `insights/matlab-simulink.html`). Für exakt
  identische URLs können in `netlify.toml` bei Bedarf Redirects ergänzt
  werden.
- Squarespace-eigene Lightbox-/Scroll-Animationen wurden nicht 1:1
  nachgebaut, sondern durch einfache, performante CSS-Übergänge (Hover,
  sanftes Bild-Zoom auf den Insight-Karten) ersetzt — funktional
  gleichwertig, wie im Briefing vorgesehen.
