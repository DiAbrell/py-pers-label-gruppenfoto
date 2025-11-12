# 🖼️ personen_label_gruppenfoto.py

Ein Python-Tool zur komfortablen Beschriftung von Gruppenfotos mit Namen oder Nummern.  
Es kombiniert **Gesichtserkennung (OpenCV Haarcascade)**, eine **interaktive Editoransicht (Tkinter + OpenCV)** und die **Erzeugung nummerierter Bilder mit Legende (Pillow)**.

Anleitung zur Nutzung von py-pers-label-gruppenfoto
---

## ✨ Hauptfunktionen

- Automatische Gesichtserkennung über OpenCV (`haarcascade_frontalface_alt2.xml`)
- Manuelles Anpassen, Verschieben, Hinzufügen und Löschen von Boxen
- Umschalten zwischen **„Reihenmodus“** und **„Single-Row-Modus“** (`r`-Taste)
- Dynamische Einstellung der Reihen-Toleranz über `+ / -`
- Export:
  - nummeriertes Bild (`_nummeriert.jpg`)
  - optional mit Legende (`_mit_legende.jpg`)
  - Begleit-Dateien (`_legende.csv` + `_legende.txt`)
- Tkinter-GUI zur Eingabe oder Korrektur der Personennamen
- Unicode-fähige Textdarstellung (Umlaute, internationale Namen)
- Anpassbare Schrift, Farbe, Position und Badge-Form

---

## 🚀 Aufruf

```bash
python personen_label_gruppenfoto.py <bilddatei> [optionen]
```

Beispiele:
- Standard Aufruf für ein neues Bild:
```bash
python personen_label_gruppenfoto.py bild.jpg 
```
- Aufruf eine bestehende Nummerierung und die Bezeichnungen bearbeiten:
```bash
python personen_label_gruppenfoto.py bild.jpg --skip-detection
```



---

## ⚙️ Parameterübersicht

| Parameter | Typ / Default | Beschreibung |
|------------|----------------|---------------|
| **image** | Datei (Pfad) | Eingabebild (Pfad zur JPG-Datei) |
| `--boxes-csv` | String, `""` | Pfad zu bestehender Box-CSV (z. B. aus früherem Lauf) |
| `--skip-detection` | Flag | Überspringt automatische Gesichtserkennung |
| `--no-box-editor` | Flag | Öffnet keinen Box-Editor (z. B. für Batch-Läufe) |
| `--keep-ids-in-editor` | Flag | Bewahrt bestehende ID-Reihenfolge beim Editieren |
| `--show-ids-in-editor` | Bool, `True` | Zeigt Live-IDs 1 .. N im Editor an |
| `--label-mode` | Auswahl: `number`, `both`, `name` – *Default:* `number` | Anzeige: nur Nummer, nur Name oder beides |
| `--append-legend` | Flag (True) | Legendenbild automatisch anhängen |
| `--legend-note` | String | Hinweistext unter der Legende |
| `--label-pos` | `below` / `above` | Position der Labels |
| `--no-green-boxes` | Flag (True) | Versteckt grüne Boxen im Endbild |
| `--row-tol` | Float, `0.75` | Toleranzfaktor für Reihenerkennung |
| `--force-single-row` | Flag | Sortierung strikt links→rechts (Standard ist aktiv) |
| `--detect-scale` | Float, `1.1` | Skalierungsfaktor der Haarcascade |
| `--detect-min-neigh` | Int, `5` | Mindestnachbarn für Erkennung |
| `--detect-min-size` | Int, `40` | Minimale Gesichtsgröße in Pixeln |
| `--cascade` | Auswahl: `default`, `alt2`, `profile` – *Default:* `alt2` | Haarcascade-Typ |
| `--font-path` | Pfad, leer | Optionaler Font (TTF oder OTF) |
| `--font-scale` | Float, `0.9` | Schriftgröße (relativ zur Bildhöhe) |
| `--font-thickness` | Int, `2` | Schriftstärke |
| `--badge-pad` | Int, `6` | Innenabstand im Badge |
| `--verbose` | Flag | Zusätzliche Konsolenausgabe (Debug) |

---

## 🖱️ Tastatursteuerung im Editor

| Taste | Funktion |
|--------|-----------|
| `LMB` | Neue Box ziehen oder Box verschieben |
| `RMB` | Box löschen |
| `r` | Modus umschalten (Reihen ↔ Single-Row) |
| `+` / `-` | Reihentoleranz anpassen |
| `s` | Speichern und schließen |
| `q` / `ESC` | Abbrechen / Schließen |

---

## 🧾 Ausgabe-Dateien

Nach erfolgreichem Durchlauf entstehen (im selben Verzeichnis wie das Eingabebild):

| Dateiname | Inhalt |
|------------|--------|
| `<name>_nummeriert.jpg` | nummeriertes Gruppenfoto |
| `<name>_mit_legende.jpg` | Gruppenfoto inkl. Legende unten |
| `<name>_legende.csv` | Positionsdaten (id, name, x, y, w, h) |
| `<name>_legende.txt` | Lesbare Text-Legende (ID: Name) |

---

## 💡 Hinweise

- Das Skript nutzt OpenCV (`cv2`), Pillow (`PIL`), NumPy und Tkinter (Standard in Python enthalten).
- Beim ersten Start kann das automatische Laden der Haarcascade etwas dauern.
- Wenn kein Font gefunden wird, bitte per `--font-path` manuell angeben, z. B.:
  ```bash
  --font-path "C:\Windows\Fonts\arial.ttf"
  ```

---

## 🧰 Installation

```bash
pip install opencv-python pillow numpy
```

---

## 🧑‍💻 Autor

**Dieter Abrell**, Stuttgart  
OpenCV / Tkinter / Pillow basierte Lösung für genealogische und historische Gruppenfotos.

---

*(Stand: 2025-11)*
