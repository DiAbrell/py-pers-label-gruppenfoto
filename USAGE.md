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

## 4. Lizenzhinweise
- **Code:** GPL v3  
- **Beispielmaterial (Foto):** Jason Krüger für Wikimedia Deutschland e. V., Lizenz CC BY-SA 4.0 https://de.m.wikipedia.org/wiki/Datei:9._Pr%C3%A4sidium_von_Wikimedia_Deutschland_e._V.jpg
Vorsitzende: Alice Wiegand,  Schatzmeisterin: Friederike von Borries, 6 Beisitzende: Jens Ohlig, Kamran Salimi, Nora Circosta, Larissa Borck, Raimond Spekking, Valerie Mocker