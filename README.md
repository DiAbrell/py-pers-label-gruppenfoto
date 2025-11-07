# py-pers-label-gruppenfoto
Ein Python-Skript, das Gesichter auf Gruppenfotos erkennt, mit Nummern versieht und eine Legende dazu mit Namen unterhalb des Bildes erstellt.
Die Namen dder Personen zu den Nummern sind über eine Oberfläche eingebbar, werden in csv/txt-Dateien gespeichert. Bei erneutem Aufruf können Namen und Legendentext ergänzt werden.
Es ist jeweils möglich mit einem Schalter auszuwählen, ob die Nummerierungen oberhalb, oder unterhalb der Gesichter postioniert sind, auch ob nur die Nummer oder auch die Namen dort bei den Gesichtern stehen.
Ideal für Vereins-, Schul- oder Familienfotos.

Verwendete Bibliotheken: OpenCV (Gesichtserkennung, interaktive Box-Bearbeitung) und Tkinter-GUI (Namenseingabe, Steuerung Ausgabeparamter)
Erforderlich: Python ≥ 3.8  mit Installation der erforderliche Bibliotheken: pip install opencv-python pillow numpy
