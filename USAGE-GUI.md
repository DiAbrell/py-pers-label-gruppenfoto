# 🧭 USAGE-GUI — Gruppenfoto Labeling Starter (Windows)

Dieses Dokument beschreibt die Nutzung der beiden GUI-Starter für das Tool  
[`personen_label_gruppenfoto.py`](personen_label_gruppenfoto.py):

- `gruppenfoto_gui.bat` – Windows-Batch-Starter  
- `gruppenfoto_gui.ps1` – PowerShell-Starter  

Beide dienen dazu, das Python-Skript komfortabel mit einem Doppelklick zu starten,  
ohne dass man Parameter auf der Kommandozeile eingeben muss.

---

## 📁 1. Ordnerstruktur

Typische Projektstruktur:

```
D:\Python\plg\
│
├── personen_label_gruppenfoto.py
├── gruppenfoto_gui.bat
├── gruppenfoto_gui.ps1
├── bild.jpg                ← Beispielbild
└── _legende.csv / .txt     ← (optional)
```

---

## ▶️ 2. Startmöglichkeiten

### Variante A – Batch-Datei  
**Doppelklick auf `gruppenfoto_gui.bat`**

- startet die PowerShell-Version im gleichen Ordner,
- prüft, ob Python installiert ist,
- öffnet eine einfache GUI-Auswahl, mit der ein Bild gewählt und das Label-Tool gestartet werden kann.

### Variante B – PowerShell-Datei  
**Rechtsklick → „Mit PowerShell ausführen“ auf `gruppenfoto_gui.ps1`**

- bietet dieselbe Funktion wie die BAT-Datei, nur direkter.  
- ideal, wenn man PowerShell-Skripte häufiger nutzt oder anpassen will.

---

## ⚙️ 3. Ablauf in der GUI

1. Nach dem Start erscheint ein Dateidialog:  
   → gewünschtes **Gruppenfoto (.jpg/.png)** auswählen.

2. Das Skript startet:
   ```
   python personen_label_gruppenfoto.py <ausgewähltes_bild> --force-single-row
   ```

3. Es öffnet sich der **Box-Editor** (OpenCV-Fenster):
   - grüne Rechtecke markieren automatisch erkannte Gesichter  
   - IDs erscheinen **unterhalb der Boxen**
   - mit der Taste **r** kann zwischen „Reihenmodus“ und „Single-Row“ gewechselt werden  
   - mit **+ / −** lässt sich die Reihentoleranz anpassen

4. Nach dem Schließen des Editors öffnet sich die **Tkinter-GUI**,  
   in der die Namen zu den IDs eingetragen werden können.

5. Mit „**Speichern & Rendern**“ werden die folgenden Dateien erzeugt:
   ```
   bild_legende.csv
   bild_legende.txt
   bild_nummeriert.jpg
   bild_mit_legende.jpg
   ```

---

## 🧩 4. Parameter in den Starterdateien

### 🔸 gruppenfoto_gui.bat
- Prüft, ob `python.exe` gefunden wird.
- Ruft standardmäßig auf:
  ```bat
  powershell -ExecutionPolicy Bypass -File "%~dp0gruppenfoto_gui.ps1" %*
  ```
- Damit wird die PowerShell-Version immer im selben Ordner ausgeführt.

### 🔸 gruppenfoto_gui.ps1
- Öffnet einen Dateiauswahldialog:
  ```powershell
  $p = (Get-Item -Path (Read-OpenFileDialog "JPEG|*.jpg;*.jpeg;*.png"))
  ```
- Übergibt den gewählten Pfad an:
  ```powershell
  python personen_label_gruppenfoto.py $p.FullName --force-single-row
  ```
- Optional kann die Zeile angepasst werden, um Parameter zu ergänzen, z. B.:
  ```powershell
  python personen_label_gruppenfoto.py $p.FullName --skip-detection --append-legend
  ```

---

## 💡 5. Tipps

- Beide Dateien sollten im gleichen Ordner liegen wie das Python-Skript.  
- Wenn beim Start Sicherheitswarnungen erscheinen („Ausführung von Skripts deaktiviert“):  
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  ```
- In Batch-Dateien **keine Anführungszeichen oder Pfade ändern**, außer man weiß genau, was man tut.

---

## 🧑‍💻 Autor

**Dieter Abrell**, Stuttgart  
Hilfsskripte für das Python-Tool `personen_label_gruppenfoto.py`  
zur komfortablen Windows-Nutzung (GUI-Start ohne Kommandozeile).

*(Stand: 2025-11)*
