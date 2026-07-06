# Briefing: Nachbau sara-hofmann.de als statische Website

## Ziel
Die bestehende Squarespace-Website **https://www.sara-hofmann.de/** soll als eigenständige, statische HTML/CSS/JS-Website nachgebaut werden — ohne laufende Squarespace-Kosten, voll portierbar, hostbar auf Netlify (oder jedem anderen statischen Hoster).

**Zielverzeichnis:** `F:\WebsiteSara`

## Vorgehen (bitte in dieser Reihenfolge)

1. **Analyse-Phase**
   - Live-Seite `https://www.sara-hofmann.de/` besuchen (Browser-Tool nutzen, falls verbunden — sonst Screenshots vom Nutzer anfordern)
   - Alle Unterseiten durchgehen und Struktur, Design (Farben, Schriftarten, Abstände, Layout-Raster), Bilder und Texte dokumentieren
   - Mobile Ansicht separat prüfen (Responsive-Verhalten)
   - Am Ende der Analyse eine kurze Zusammenfassung der gefundenen Struktur und des Design-Systems ausgeben, bevor mit dem Bauen begonnen wird

2. **Projekt-Setup in `F:\WebsiteSara`**
   - Struktur: `index.html`, ein Ordner `pages/` oder Multi-Page-Setup (kein Framework nötig, reines HTML/CSS/JS)
   - Ordner `assets/` für Bilder, `assets/fonts/` falls nötig, `css/`, `js/`
   - `README.md` mit kurzer Erklärung, wie man die Seite lokal öffnet/testet und wie der Netlify-Deploy funktioniert

3. **Seitenstruktur nachbauen** (bekannter Stand, bitte bei der Live-Analyse verifizieren/ergänzen):
   - Startseite (inkl. Blog-Vorschau "Insights")
   - Über mich
   - Consulting
   - Dozententätigkeit
   - Nachhilfe
   - Kontakt (mit Kontaktformular)
   - Impressum, Datenschutz, AGB
   - CV als PDF zum Download (Datei vom Nutzer anfordern, falls nicht öffentlich zugänglich)
   - Sprachumschalter (Deutsch/ggf. weitere Sprache) — falls nur Deutsch aktiv genutzt wird, das UI-Element trotzdem vorsehen, aber Priorität niedrig ansetzen

4. **Design-Umsetzung**
   - Farbpalette, Typografie und Layout so nah wie möglich am Original nachbauen
   - Falls Squarespace eine Premium-Schrift (z. B. über Adobe Fonts/Typekit) nutzt, eine passende Google-Fonts-Alternative wählen und das im README dokumentieren
   - Responsive Design (Mobile-first oder mind. saubere Breakpoints für Mobile/Tablet/Desktop)
   - Sanfte Scroll-/Hover-Animationen nach Bedarf (Vanilla JS oder GSAP, falls per CDN eingebunden)

5. **Kontaktformular**
   - Von Squarespace-Formular auf **Netlify Forms** umstellen (`<form name="contact" method="POST" data-netlify="true">` + Honeypot-Feld gegen Spam)
   - Erfolgsseite/-meldung nach Absenden einbauen

6. **Content-Übernahme**
   - Alle Texte 1:1 von der Live-Seite übernehmen (es ist der eigene Content der Seitenbetreiberin, keine Urheberrechtsfrage)
   - Bilder in bester verfügbarer Qualität sichern und in `assets/` einbinden, Dateigrößen für Web optimieren (komprimieren, falls nötig)

7. **SEO-Grundlagen**
   - Meta-Title, Meta-Description pro Seite
   - Semantisches HTML (richtige Heading-Hierarchie, alt-Texte für Bilder)
   - `sitemap.xml` und `robots.txt` generieren

8. **Abschluss**
   - Kurzer Test-Durchlauf: alle internen Links, Formular-Versand, Mobile-Ansicht
   - Deploy-Anleitung für Netlify im README (Drag&Drop-Ordner-Upload oder Git-Verknüpfung)
   - Hinweis auf DNS-Umstellung: MX-Records (E-Mail, z. B. bei IONOS) unbedingt unangetastet lassen, nur A-/CNAME-Records auf Netlify umstellen

## Wichtige Einschränkungen
- Kein 1:1-Pixel-Klon bei Squarespace-eigenen Effekten (z. B. bestimmte Lightbox-Galerien) — funktional gleichwertige, sauber Vanilla-JS-basierte Lösung ist ausreichend
- Kein Backend/CMS — reine statische Seite
- Falls die Seite einen Mitglieder- oder Buchungsbereich hat, das separat melden statt zu versuchen, es "nachzubauen" — das müsste extra aufgesetzt werden

## Output
Fertiges, lauffähiges Projekt in `F:\WebsiteSara`, lokal per Doppelklick auf `index.html` oder via einfachem lokalen Server testbar, deploy-fertig für Netlify.
