# Anleitung zur Nutzung von py-pers-label-gruppenfoto

## 1. Erkennung und Bearbeitung der Boxen
Starte das Skript mit:
```bash
python personen_label_gruppenfoto.py gruppenbild.jpg
```

### Steuerung in der GUI
- **Linksklick + Ziehen außerhalb einer Box** → neue Box aufziehen  
- **Linksklick + Ziehen innerhalb einer Box** → Box verschieben  
- **Rechtsklick auf Box** → Box löschen  
- **Taste r** → Reihenmodus umschalten  
  - *Reihenmodus:* von oben nach unten, links nach rechts  
  - *Single-Row-Modus:* durchgehend links nach rechts  
- **Taste s** → Speichern und schließen  
- **q oder ESC** → Abbrechen (die aktuelle Anordnung bleibt trotzdem gespeichert)

Die Boxen und IDs werden in einer CSV-Datei gespeichert (`gruppenbild_legende.csv`).

---

## 2. Nachträgliches Ergänzen oder Korrigieren von Namen
Die Namen sind in `gruppenbild_legende.csv` gespeichert.  
Beispiel:

```csv
id,name,x,y,w,h
1,Max,120,80,90,90
2,Erika,250,82,88,88
3,,380,85,92,92
```

- Tippfehler einfach direkt in der CSV korrigieren  
- Fehlende Namen ergänzen (leere Felder ausfüllen)  

Danach Skript erneut starten mit:

```bash
python personen_label_gruppenfoto.py gruppenbild.jpg --skip-detection --names-csv gruppenbild_legende.csv --append-legend
```

Das Originalbild wird neu mit den korrigierten Namen beschriftet.

---

## 3. Steuerung, was im Bild angezeigt wird
Mit `--label-mode` kannst du festlegen:

- `--label-mode number` → nur Nummern  
- `--label-mode name` → nur Namen  
- `--label-mode both` (Standard) → Nummer + Name  

Beispiel:

```bash
python personen_label_gruppenfoto.py gruppenbild.jpg --skip-detection --names-csv gruppenbild_legende.csv --label-mode name
```

---


## 4. Badge-Formen (neu in v3f)
Mit `--badge-shape` lässt sich die Form der Nummernbadges ändern:

- `rect` (Standard): schwarzer Hintergrund in Rechteckform
- `circle`: runde Nummern-Badges (ähnlich wie Nummernschilder)

Beispiel:
```bash
python personen_label_gruppenfoto_v3f.py gruppenbild.jpg --badge-shape circle
```

## 5. Preset für A5-Querformat (neu in v3f)
Mit `--preset a5` werden automatisch optimierte Einstellungen für Druckausgabe auf A5 quer (ca. 2480×1748 px bei 300 dpi) gesetzt.
Dies entspricht folgenden Parametern:

```
--font-scale 1.4 --font-thickness 3 --badge-pad 8 --legend-title-scale 1.3 --legend-font-scale 1.0 --legend-thickness 3 --legend-strip-height 320 --legend-line-height 42 --legend-col-width 450
```

Beispiel:
```bash
python personen_label_gruppenfoto_v3f.py gruppenbild.jpg --preset a5 --badge-shape circle
```

## 6. Lizenz
(verschoben aus Kapitel 4)
hinweise
- **Code:** GPL v3  
- **Beispielmaterial (Foto):** Jason Krüger für Wikimedia Deutschland e. V., Lizenz CC BY-SA 4.0 https://de.m.wikipedia.org/wiki/Datei:9._Pr%C3%A4sidium_von_Wikimedia_Deutschland_e._V.jpg
Vorsitzende: Alice Wiegand,  Schatzmeisterin: Friederike von Borries, 6 Beisitzende: Jens Ohlig, Kamran Salimi, Nora Circosta, Larissa Borck, Raimond Spekking, Valerie Mocker

## 7. Schritt-für-Schritt: Vereinsfoto mit Legende erstellen

1. **Gesichter erkennen und Bild speichern**  
   ```bash
   python personen_label_gruppenfoto_v3f.py gruppenbild.jpg
   ```  
   → Ergebnis: `gruppenbild_mit_boxes.jpg` mit Nummern über den Personen.

2. **Namen in CSV ergänzen**  
   Öffne die automatisch erzeugte `gruppenbild_legende.csv` in Excel oder einem Editor und trage die Namen zu den Nummern ein.

3. **Legende unter das Bild setzen**  
   ```bash
   python personen_label_gruppenfoto_v3f.py gruppenbild_mit_boxes.jpg      --names-csv gruppenbild_legende.csv      --append-legend --skip-detection
   ```  
   → Ergebnis: `gruppenbild_mit_legende.jpg` mit Nummern im Bild und Namensliste unten.

4. **Optional: Optik anpassen**  
   - Runde Badges: `--badge-shape circle`  
   - Größere Schrift und passende Legende für A5: `--preset a5`  
   - Einzelwerte feintunen (z. B. `--font-scale 1.2` oder `--legend-line-height 40`).

Damit hast du in wenigen Schritten ein druckbares Vereins- oder Schulbild mit eingebauter Legende.


---

## 8. Namens-Frontend mit Tkinter

Nach dem Speichern oder Bearbeiten der Boxen öffnet sich automatisch ein Fenster
(zur Eingabe/Korrektur der Personennamen).

### Funktionen
- **Scrollbare Tabelle:** zeigt alle IDs und ermöglicht das Eintragen oder Ändern der Namen.  
- **Optionen unten:**  
  - Label-Modus: *Nummer + Name*, *nur Nummer* oder *nur Name*  
  - Häkchen: *Legende anhängen*, *Runde Badges*  
  - Anpassung von Schriftgröße, Dicke, Padding  
- **Buttons:** *Speichern*, *Speichern & Rendern*, *Abbrechen*  

### Tipps
- Mit *Speichern* werden CSV/TXT sofort geschrieben.  
- Mit *Speichern & Rendern* wird zusätzlich ein neues Bild erzeugt
  (Nummern/Namen und ggf. Legende).  
- Mit `--no-names-gui` lässt sich die GUI deaktivieren (z.B. für reinen Batch-Lauf).  
- Mit `--skip-detection` kann man direkt aus vorhandenen CSV-Dateien neu rendern,
  ohne erneut Boxen zu bearbeiten.

Damit entfällt das mühsame parallele Editieren von CSV-Datei und Bild.
