#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
personen_label_gruppenfoto.py

In: github.com/DiAbrell/py-pers-label-gruppenfoto

Neu in v3d:
- --skip-detection  -> überspringt Erkennung & GUI; lädt Boxen aus CSV und rendert sofort neu
- --boxes-csv PATH  -> CSV mit Spalten id,name,x,y,w,h (wenn nicht angegeben, wird <image>_legende.csv versucht)
- --label-mode {both,number,name} -> steuert, was im Bild steht

Weiterhin vorhanden:
- Automatik-Erkennung (Haarcascade)
- IMMER eine GUI zum Nachbearbeiten, sofern --skip-detection NICHT gesetzt ist
- Namen per --names-csv und/oder --prompt-names
- Legendenleiste (--append-legend), Anzeige (--show), Outdir-Steuerung

pip install opencv-python numpy
"""

from __future__ import annotations
import argparse
import csv
import os
import sys
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional

import cv2
import numpy as np


@dataclass
class Face:
    x: int
    y: int
    w: int
    h: int
    id: int = -1
    name: str = ""

    @property
    def center(self) -> Tuple[float, float]:
        return (self.x + self.w / 2.0, self.y + self.h / 2.0)


def detect_faces(
    image_bgr,
    cascade_path: str,
    scale_factor: float = 1.2,
    min_neighbors: int = 5,
    min_size: int = 40,
    padding: int = 6,
) -> List[Face]:
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    if not os.path.exists(cascade_path):
        raise FileNotFoundError(f"Cascade nicht gefunden: {cascade_path}")

    cascade = cv2.CascadeClassifier(cascade_path)
    rects = cascade.detectMultiScale(
        gray,
        scaleFactor=scale_factor,
        minNeighbors=min_neighbors,
        minSize=(min_size, min_size),
        flags=cv2.CASCADE_SCALE_IMAGE,
    )

    faces: List[Face] = []
    H, W = gray.shape[:2]
    for (x, y, w, h) in rects:
        x2 = max(0, x - padding)
        y2 = max(0, y - padding)
        w2 = min(W - x2, w + 2 * padding)
        h2 = min(H - y2, h + 2 * padding)
        faces.append(Face(x2, y2, w2, h2))

    return faces


def _group_faces_into_rows_from_rects(rects: List[Tuple[int,int,int,int]], tol_factor: float = 0.75) -> List[List[int]]:
    if not rects:
        return []
    centers_y = [y + h/2.0 for (x,y,w,h) in rects]
    hs = [h for (x,y,w,h) in rects]
    median_h = float(np.median(hs)) if hs else 1.0
    tol = max(tol_factor * median_h, 18.0)

    idxs = list(range(len(rects)))
    idxs.sort(key=lambda i: centers_y[i])

    rows: List[List[int]] = []
    current = [idxs[0]]
    base_y = centers_y[idxs[0]]
    for i in idxs[1:]:
        if abs(centers_y[i] - base_y) <= tol:
            current.append(i)
        else:
            current.sort(key=lambda j: rects[j][0])
            rows.append(current)
            current = [i]
            base_y = centers_y[i]
    current.sort(key=lambda j: rects[j][0])
    rows.append(current)
    return rows


def reorder_rects(rects: List[Tuple[int,int,int,int]], force_single: bool, tol_factor: float) -> List[Tuple[int,int,int,int]]:
    if force_single:
        return sorted(rects, key=lambda r: r[0])
    rows = _group_faces_into_rows_from_rects(rects, tol_factor=tol_factor)
    out: List[Tuple[int,int,int,int]] = []
    for row in rows:
        out.extend([rects[i] for i in row])
    return out


def draw_annotations(
    image_bgr,
    faces: List[Face],
    label_mode: str = "both",  # both, number, name
    box_color=(0, 200, 0),
    txt_color=(255, 255, 255),
    id_bg_color=(0, 0, 0),
    font_scale: float = 0.9,
    font_thickness: int = 2,
    badge_pad: int = 6,
    badge_shape: str = "rect",
):
    out = image_bgr.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX
    for f in faces:
        cv2.rectangle(out, (f.x, f.y), (f.x + f.w, f.y + f.h), box_color, thickness=2)
        if label_mode == "number":
            label = str(f.id)
        elif label_mode == "name":
            label = f.name if f.name else ""
        else:
            label = str(f.id) if not f.name else f"{f.id} {f.name}"

        if label:
            (tw, th), baseline = cv2.getTextSize(label, font, fontScale=font_scale, thickness=font_thickness)
            pad = badge_pad
            tx = f.x
            ty = max(0, f.y - 6)
            if tx + tw + 2 * pad > out.shape[1]:
                tx = max(0, out.shape[1] - (tw + 2 * pad))
            bg_top_left = (tx, max(0, ty - th - 2 * pad))
            bg_bot_right = (tx + tw + 2 * pad, ty + baseline + pad)
            cv2.rectangle(out, bg_top_left, bg_bot_right, id_bg_color, thickness=-1)
            text_org = (tx + pad, ty - baseline // 2)
            cv2.putText(out, label, text_org, font, font_scale, txt_color, thickness=font_thickness, lineType=cv2.LINE_AA)
    return out


def build_legend_image(entries, width: int, strip_height: int = 260, margin: int = 16, line_height: int = 34, col_gap: int = 48, col_width: int = 420, title_scale: float = 1.1, font_scale: float = 0.85, thickness: int = 2):
    strip = np.full((strip_height, width, 3), 255, dtype=np.uint8)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cols = max(1, (width - 2 * margin + col_gap) // (col_width + col_gap))
    lines = [f"{i}: {name if name else '—'}" for (i, name) in entries]
    per_col = int(np.ceil(len(lines) / cols))
    col_xs = [margin + c * (col_width + col_gap) for c in range(cols)]
    for idx, line in enumerate(lines):
        c = idx // per_col; r = idx % per_col
        if c >= cols: break
        x = col_xs[c]; y = margin + (r + 2) * line_height
        if y + margin > strip_height: break
        cv2.putText(strip, line, (x, y), font, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)
    title = "Legende (ID: Name)"
    cv2.putText(strip, title, (margin, margin + int(line_height * 0.7)), font, title_scale, (0, 0, 0), thickness, cv2.LINE_AA)
    return strip


def append_strip_to_image(image_bgr, strip_bgr):
    H, W = image_bgr.shape[:2]
    sh, sw = strip_bgr.shape[:2]
    if sw != W:
        strip_bgr = cv2.resize(strip_bgr, (W, sh), interpolation=cv2.INTER_AREA)
    return np.vstack([image_bgr, strip_bgr])


def save_csv_and_txt(out_stem: str, faces: List[Face]):
    csv_path = f"{out_stem}_legende.csv"
    txt_path = f"{out_stem}_legende.txt"
    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["id", "name", "x", "y", "w", "h"])
        for f in faces:
            writer.writerow([f.id, f.name, f.x, f.y, f.w, f.h])
    with open(txt_path, "w", encoding="utf-8") as fh:
        for f in faces:
            name = f.name if f.name else "—"
            fh.write(f"{f.id}: {name}\n")
    return csv_path, txt_path


def prompt_names_in_terminal(faces: List[Face]) -> None:
    print("\\nBitte Namen zu den Personen eingeben (Enter = unbekannt).")
    for f in faces:
        try:
            entered = input(f"Name für ID {f.id} (x={f.x}, y={f.y}, w={f.w}, h={f.h}): ").strip()
        except EOFError:
            entered = ""
        f.name = entered


def read_names_csv(path: str) -> Dict[int, str]:
    mapping: Dict[int, str] = {}
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if "id" not in reader.fieldnames or "name" not in reader.fieldnames:
            raise ValueError("CSV muss Spalten 'id' und 'name' enthalten.")
        for row in reader:
            try:
                i = int(row["id"])
            except Exception:
                continue
            mapping[i] = row.get("name", "").strip()
    return mapping


def read_boxes_csv(path: str) -> List[Face]:
    faces: List[Face] = []
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if not {"id","x","y","w","h"}.issubset(set(reader.fieldnames or [])):
            raise ValueError("Boxes-CSV muss Spalten id,x,y,w,h enthalten (name optional).")
        for row in reader:
            try:
                i = int(row["id"]); x=int(float(row["x"])); y=int(float(row["y"])); w=int(float(row["w"])); h=int(float(row["h"]))
            except Exception:
                continue
            nm = (row.get("name") or "").strip()
            faces.append(Face(x,y,w,h,id=i,name=nm))
    faces.sort(key=lambda f: f.id)
    return faces



def names_gui_edit(faces: List[Face], out_stem: str, img_bgr, label_mode: str, args) -> bool:
    """
    Öffnet ein PySimpleGUI-Fenster zum Eingeben/Korrigieren der Namen.
    Speichert CSV/TXT immer; optional rendert es sofort das Bild (+Legende) nach aktueller Auswahl.
    Gibt True zurück, wenn gespeichert wurde (egal ob mit oder ohne Rendern).
    """
    try:
        import PySimpleGUI as sg
    except Exception as ex:
        print("Hinweis: PySimpleGUI nicht installiert oder nicht verfügbar – falle zurück auf Terminal-Eingabe (--prompt-names).", file=sys.stderr)
        prompt_names_in_terminal(faces)
        return True

    # Layout bauen
    header = [sg.Text("ID", size=(6,1)), sg.Text("Name", size=(40,1))]
    rows = []
    for f in faces:
        rows.append([sg.Text(str(f.id), size=(6,1)), sg.Input(default_text=f.name, key=f"NAME_{f.id}", size=(42,1))])

    # Optionen unten
    opts = [
        [sg.Text("Label-Modus:"),
         sg.Combo(values=["both","number","name"], default_value=label_mode, key="LABEL_MODE", readonly=True, size=(10,1)),
         sg.Checkbox("Legende anhängen", default=getattr(args, "append_legend", False), key="APPEND_LEGEND"),
         sg.Checkbox("Runde Badges", default=(getattr(args, "badge_shape", "rect")=="circle"), key="BADGE_CIRCLE")
        ],
        [sg.Text("Schriftgröße:"), sg.Input(str(getattr(args, "font_scale", 0.9)), key="FONT_SCALE", size=(6,1)),
         sg.Text("Dicke:"), sg.Input(str(getattr(args, "font_thickness", 2)), key="FONT_THICK", size=(4,1)),
         sg.Text("Badge-Pad:"), sg.Input(str(getattr(args, "badge_pad", 6)), key="BADGE_PAD", size=(4,1))],
        [sg.Button("Speichern"), sg.Button("Speichern & Rendern"), sg.Button("Abbrechen")]
    ]

    layout = [[sg.Column([header]+rows, scrollable=True, vertical_scroll_only=True, size=(520, 360))],
              [sg.Frame("Optionen", opts)]]

    win = sg.Window("Namen eingeben / korrigieren", layout, finalize=True)

    saved = False
    while True:
        ev, vals = win.read()
        if ev in (sg.WIN_CLOSED, "Abbrechen"):
            break
        if ev in ("Speichern", "Speichern & Rendern"):
            # Namen übernehmen
            for f in faces:
                f.name = vals.get(f"NAME_{f.id}", "").strip()

            # CSV/TXT schreiben
            csv_path, txt_path = save_csv_and_txt(out_stem, faces)
            print(f"CSV gespeichert: {csv_path}")
            print(f"TXT gespeichert: {txt_path}")
            saved = True

            if ev == "Speichern & Rendern":
                try:
                    # Parameter einsammeln
                    label_mode_sel = vals.get("LABEL_MODE", label_mode)
                    append_legend = bool(vals.get("APPEND_LEGEND", False))
                    badge_shape = "circle" if vals.get("BADGE_CIRCLE", False) else "rect"
                    # Fonts
                    try:
                        fscale = float(vals.get("FONT_SCALE", getattr(args, "font_scale", 0.9)))
                    except: fscale = getattr(args, "font_scale", 0.9)
                    try:
                        fthick = int(vals.get("FONT_THICK", getattr(args, "font_thickness", 2)))
                    except: fthick = getattr(args, "font_thickness", 2)
                    try:
                        bpad = int(vals.get("BADGE_PAD", getattr(args, "badge_pad", 6)))
                    except: bpad = getattr(args, "badge_pad", 6)

                    anno = draw_annotations(img_bgr, faces, label_mode=label_mode_sel,
                                            font_scale=fscale, font_thickness=fthick,
                                            badge_pad=bpad, badge_shape=badge_shape)
                    anno_path = f"{out_stem}_nummeriert.jpg"
                    cv2.imwrite(anno_path, anno, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
                    print(f"Annotiertes Bild gespeichert: {anno_path}")

                    if append_legend:
                        entries = [(f.id, f.name) for f in faces]
                        strip = build_legend_image(entries, width=anno.shape[1],
                                                   strip_height=getattr(args, "legend_strip_height", 260),
                                                   line_height=getattr(args, "legend_line_height", 34),
                                                   col_gap=getattr(args, "legend_col_gap", 48),
                                                   col_width=getattr(args, "legend_col_width", 420),
                                                   title_scale=getattr(args, "legend_title_scale", 1.1),
                                                   font_scale=getattr(args, "legend_font_scale", 0.85),
                                                   thickness=getattr(args, "legend_thickness", 2))
                        combined = append_strip_to_image(anno, strip)
                        legend_path = f"{out_stem}_mit_legende.jpg"
                        cv2.imwrite(legend_path, combined, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
                        print(f"Bild mit Legende gespeichert: {legend_path}")
                except Exception as ex:
                    print(f"Fehler beim Rendern aus dem GUI: {ex}", file=sys.stderr)
            # Bei einfachem Speichern bleiben wir im Fenster, falls noch Feinschliff nötig.
            if ev == "Speichern & Rendern":
                break

    win.close()
    return saved



def names_gui_edit(faces: List[Face], out_stem: str, img_bgr, label_mode_default: str, args) -> bool:
    """
    Tkinter-Frontend zum Eingeben/Korrigieren der Namen.
    - Zeigt eine scrollbare Liste: ID | Eingabefeld Name
    - Unten: Optionen (Label-Mode, Legende anhängen, runde Badges, Schriftgrößen)
    - Buttons: Speichern  /  Speichern & Rendern  /  Abbrechen
    Gibt True zurück, wenn etwas gespeichert wurde.
    """
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
    except Exception as ex:
        print("Hinweis: Konnte Tkinter nicht laden. Fallback: Terminal-Eingabe (--prompt-names).", file=sys.stderr)
        prompt_names_in_terminal(faces)
        return True

    root = tk.Tk()
    root.title("Namen eingeben / korrigieren")

    # --- Scrollbarer Bereich für Eingaben ---
    container = ttk.Frame(root, padding=8)
    container.grid(row=0, column=0, sticky="nsew")
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    canvas = tk.Canvas(container, width=560, height=380)
    vsb = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    frame = ttk.Frame(canvas)
    frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0,0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=vsb.set)

    canvas.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    container.rowconfigure(0, weight=1)
    container.columnconfigure(0, weight=1)

    # Header
    ttk.Label(frame, text="ID", width=6).grid(row=0, column=0, sticky="w", padx=(4,8), pady=4)
    ttk.Label(frame, text="Name", width=40).grid(row=0, column=1, sticky="w", padx=(4,8), pady=4)

    name_vars = {}
    for idx, f in enumerate(faces, start=1):
        ttk.Label(frame, text=str(f.id), width=6).grid(row=idx, column=0, sticky="w", padx=(4,8), pady=2)
        var = tk.StringVar(value=f.name)
        ent = ttk.Entry(frame, textvariable=var, width=48)
        ent.grid(row=idx, column=1, sticky="we", padx=(4,8), pady=2)
        name_vars[f.id] = var

    # --- Optionen unten ---
    opts = ttk.Frame(root, padding=(8,0,8,8))
    opts.grid(row=1, column=0, sticky="ew")
    root.columnconfigure(0, weight=1)

    ttk.Label(opts, text="Label-Modus:").grid(row=0, column=0, sticky="w")
    label_mode_var = tk.StringVar(value=label_mode_default or "both")
    ttk.Radiobutton(opts, text="Nummer + Name", variable=label_mode_var, value="both").grid(row=0, column=1, sticky="w")
    ttk.Radiobutton(opts, text="nur Nummer", variable=label_mode_var, value="number").grid(row=0, column=2, sticky="w")
    ttk.Radiobutton(opts, text="nur Name", variable=label_mode_var, value="name").grid(row=0, column=3, sticky="w")

    append_legend_var = tk.BooleanVar(value=getattr(args, "append_legend", False))
    ttk.Checkbutton(opts, text="Legende anhängen", variable=append_legend_var).grid(row=1, column=1, sticky="w")

    circle_var = tk.BooleanVar(value=(getattr(args, "badge_shape", "rect") == "circle"))
    ttk.Checkbutton(opts, text="Runde Badges", variable=circle_var).grid(row=1, column=2, sticky="w")

    # Schrift-Optionen
    ttk.Label(opts, text="Schriftgröße:").grid(row=2, column=0, sticky="e")
    font_scale_var = tk.StringVar(value=str(getattr(args, "font_scale", 0.9)))
    ttk.Entry(opts, textvariable=font_scale_var, width=6).grid(row=2, column=1, sticky="w")

    ttk.Label(opts, text="Dicke:").grid(row=2, column=2, sticky="e")
    font_thick_var = tk.StringVar(value=str(getattr(args, "font_thickness", 2)))
    ttk.Entry(opts, textvariable=font_thick_var, width=4).grid(row=2, column=3, sticky="w")

    ttk.Label(opts, text="Badge-Pad:").grid(row=2, column=4, sticky="e")
    badge_pad_var = tk.StringVar(value=str(getattr(args, "badge_pad", 6)))
    ttk.Entry(opts, textvariable=badge_pad_var, width=4).grid(row=2, column=5, sticky="w")

    # Buttons
    btns = ttk.Frame(root, padding=8)
    btns.grid(row=2, column=0, sticky="e")
    save_btn = ttk.Button(btns, text="Speichern")
    save_render_btn = ttk.Button(btns, text="Speichern & Rendern")
    cancel_btn = ttk.Button(btns, text="Abbrechen")
    save_btn.grid(row=0, column=0, padx=4)
    save_render_btn.grid(row=0, column=1, padx=4)
    cancel_btn.grid(row=0, column=2, padx=4)

    saved_flag = {"saved": False}

    def do_save(render: bool):
        # Namen übernehmen
        for f in faces:
            f.name = name_vars[f.id].get().strip()
        # CSV/TXT schreiben
        csv_path, txt_path = save_csv_and_txt(out_stem, faces)
        saved_flag["saved"] = True
        try:
            if render:
                # Einstellungen aus UI
                try:
                    fscale = float(font_scale_var.get())
                except:
                    fscale = getattr(args, "font_scale", 0.9)
                try:
                    fthick = int(font_thick_var.get())
                except:
                    fthick = getattr(args, "font_thickness", 2)
                try:
                    bpad = int(badge_pad_var.get())
                except:
                    bpad = getattr(args, "badge_pad", 6)
                badge_shape = "circle" if circle_var.get() else "rect"
                lmode = label_mode_var.get()

                anno = draw_annotations(img_bgr, faces, label_mode=lmode,
                                        font_scale=fscale, font_thickness=fthick,
                                        badge_pad=bpad, badge_shape=badge_shape)
                anno_path = f"{out_stem}_nummeriert.jpg"
                cv2.imwrite(anno_path, anno, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
                if append_legend_var.get():
                    entries = [(f.id, f.name) for f in faces]
                    strip = build_legend_image(entries, width=anno.shape[1],
                                               strip_height=getattr(args, "legend_strip_height", 260),
                                               line_height=getattr(args, "legend_line_height", 34),
                                               col_gap=getattr(args, "legend_col_gap", 48),
                                               col_width=getattr(args, "legend_col_width", 420),
                                               title_scale=getattr(args, "legend_title_scale", 1.1),
                                               font_scale=getattr(args, "legend_font_scale", 0.85),
                                               thickness=getattr(args, "legend_thickness", 2))
                    combined = append_strip_to_image(anno, strip)
                    legend_path = f"{out_stem}_mit_legende.jpg"
                    cv2.imwrite(legend_path, combined, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        except Exception as ex:
            messagebox.showerror("Fehler", f"Fehler beim Rendern: {ex}")
        finally:
            if render:
                root.destroy()
            else:
                messagebox.showinfo("Gespeichert", "CSV/TXT gespeichert.")

    save_btn.configure(command=lambda: do_save(False))
    save_render_btn.configure(command=lambda: do_save(True))
    cancel_btn.configure(command=root.destroy)

    root.mainloop()
    return saved_flag["saved"]


def edit_boxes_gui(img_bgr, rects, mode_force_single, tol_factor, font_scale: float = 0.9, font_thickness: int = 2):
    if rects is None: rects=[]
    dragging=False; moving_idx=-1; drag_start=(0,0); move_offset=(0,0); current_rect=None
    win="Bearbeiten  [LMB ziehen: neu | LMB auf Box: verschieben | RMB: loeschen | r: Modus | s: speichern | q/ESC: schliessen]"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)

    def inside(r, px, py):
        x,y,w,h=r; return x<=px<=x+w and y<=py<=y+h
    def on_mouse(event,x,y,flags,param):
        nonlocal dragging,moving_idx,drag_start,move_offset,current_rect,rects
        if event==cv2.EVENT_LBUTTONDOWN:
            moving_idx=-1
            for i,r in enumerate(rects):
                if inside(r,x,y): moving_idx=i; break
            dragging=True; drag_start=(x,y)
            if moving_idx>=0:
                rx,ry,rw,rh=rects[moving_idx]; move_offset=(x-rx,y-ry); current_rect=None
            else: current_rect=(x,y,0,0)
        elif event==cv2.EVENT_MOUSEMOVE and dragging:
            if moving_idx>=0:
                ox,oy=move_offset; rx,ry,rw,rh=rects[moving_idx]
                rects[moving_idx]=(x-ox, y-oy, rw, rh)
            else:
                x0,y0,_,_=current_rect; current_rect=(min(x0,x),min(y0,y),abs(x-x0),abs(y-y0))
        elif event==cv2.EVENT_LBUTTONUP:
            if moving_idx>=0: moving_idx=-1
            else:
                if current_rect and current_rect[2]>10 and current_rect[3]>10: rects.append(current_rect)
            dragging=False; current_rect=None
        elif event==cv2.EVENT_RBUTTONDOWN:
            for r in rects[:]:
                if inside(r,x,y): rects.remove(r); break
    cv2.setMouseCallback(win, on_mouse)

    force_single=mode_force_single
    while True:
        ordered=reorder_rects(rects, force_single, tol_factor)
        vis=img_bgr.copy()
        font=cv2.FONT_HERSHEY_SIMPLEX
        for i,(x,y,w,h) in enumerate(ordered,1):
            cv2.rectangle(vis,(int(x),int(y)),(int(x+w),int(y+h)),(0,255,0),2)
            label=str(i); (tw,th),base=cv2.getTextSize(label,font,font_scale,font_thickness)
            tx,ty=int(x),max(0,int(y)-6)
            cv2.rectangle(vis,(tx,max(0,ty-th-6)),(tx+tw+12,ty+6),(0,0,0),-1)
            cv2.putText(vis,label,(tx+6,ty),font,font_scale,(255,255,255),font_thickness,cv2.LINE_AA)
        if current_rect:
            x,y,w,h=current_rect
            cv2.rectangle(vis,(int(x),int(y)),(int(x+w),int(y+h)),(0,0,255),1)
        mode_txt="Modus: Single-Row (links->rechts)" if force_single else "Modus: Reihen (oben->unten, links->rechts)"
        cv2.putText(vis, mode_txt, (10,24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (20,20,20), 2, cv2.LINE_AA)
        cv2.imshow(win, vis)
        k=cv2.waitKey(20)&0xFF
        if k in [27, ord('q')]: rects=ordered; break
        if k==ord('r'): force_single=not force_single
        if k==ord('s'): rects=ordered; break
    cv2.destroyWindow(win)
    return rects, force_single


def main():
    ap = argparse.ArgumentParser(description="Gruppenfoto: Erkennung + (optionale) GUI + CSV-Re-Render + flexible Labels.")
    ap.add_argument("image")
    ap.add_argument("--outdir", default="")

    ap.add_argument("--skip-detection", action="store_true", help="Erkennung & GUI überspringen; Boxen aus CSV laden und sofort neu rendern.")
    ap.add_argument("--boxes-csv", default="", help="CSV mit id,name,x,y,w,h (wenn leer, wird <image>_legende.csv versucht).")

    ap.add_argument("--label-mode", choices=["both","number","name"], default="both", help="Was im Bild steht: both, number oder name.")
    ap.add_argument("--append-legend", action="store_true")
    ap.add_argument("--no-names-gui", action="store_true", help="Kein Namens-Frontend nach der Box-Bearbeitung öffnen.")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--no-names-on-image", dest="no_names_on_image", action="store_true",
                    help="(veraltet) entspricht --label-mode number, wenn keine Namen vorhanden sind.")

    ap.add_argument("--prompt-names", action="store_true")
    ap.add_argument("--names-csv", default="")

    ap.add_argument("--scale-factor", type=float, default=1.2)
    ap.add_argument("--min-neighbors", type=int, default=5)
    ap.add_argument("--min-size", type=int, default=40)
    ap.add_argument("--padding", type=int, default=6)
    ap.add_argument("--row-tol", type=float, default=0.75)
    ap.add_argument("--force-single-row", action="store_true")
    ap.add_argument("--face-cascade", default=os.path.join(cv2.data.haarcascades,"haarcascade_frontalface_default.xml"))

    # Neue Optionen für Badges und Presets
    ap.add_argument("--badge-shape", choices=["rect", "circle"], default="rect",
                    help="Form der Nummernbadges: rechteckig (rect) oder rund (circle)")
    ap.add_argument("--preset", choices=["a5"], default=None,
                    help="Preset für Ausgabegrößen, z. B. a5 für A5 quer.")
    # Schrift & Darstellung
    ap.add_argument("--font-scale", type=float, default=0.9, help="Schriftgröße für IDs/Namen im Bild (Standard 0.9).")
    ap.add_argument("--font-thickness", type=int, default=2, help="Schriftstärke für IDs/Namen im Bild (Standard 2).")
    ap.add_argument("--badge-pad", type=int, default=6, help="Innenabstand der Text-Hinterlegung (Standard 6).")
    ap.add_argument("--legend-title-scale", type=float, default=1.1, help="Schriftgröße für Legenden-Überschrift (Standard 1.1).")
    ap.add_argument("--legend-font-scale", type=float, default=0.85, help="Schriftgröße für Legendenzeilen (Standard 0.85).")
    ap.add_argument("--legend-thickness", type=int, default=2, help="Schriftstärke in der Legende (Standard 2).")
    ap.add_argument("--legend-strip-height", type=int, default=260, help="Höhe der Legendenleiste in Pixel (Standard 260).")
    ap.add_argument("--legend-line-height", type=int, default=34, help="Zeilenhöhe in der Legende (Standard 34).")
    ap.add_argument("--legend-col-gap", type=int, default=48, help="Spaltenabstand in der Legende (Standard 48).")
    ap.add_argument("--legend-col-width", type=int, default=420, help="Zielbreite pro Textspalte in der Legende (Standard 420).")

    args = ap.parse_args()
    # Preset-Anpassungen
    if args.preset == "a5":
        args.font_scale = 1.4
        args.font_thickness = 3
        args.badge_pad = 8
        args.legend_title_scale = 1.3
        args.legend_font_scale = 1.0
        args.legend_thickness = 3
        args.legend_strip_height = 320
        args.legend_line_height = 42
        args.legend_col_width = 450


    if not os.path.exists(args.image):
        print(f"Eingabedatei nicht gefunden: {args.image}", file=sys.stderr); sys.exit(1)
    img = cv2.imread(args.image)
    if img is None:
        print(f"Konnte Bild nicht laden (JPG/PNG?): {args.image}", file=sys.stderr); sys.exit(1)

    in_dir, in_name = os.path.split(args.image)
    if not in_dir:
        in_dir = os.getcwd()
    out_dir = args.outdir if args.outdir else in_dir
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    stem, _ = os.path.splitext(in_name)
    out_stem = os.path.join(out_dir, stem)

    faces: List[Face] = []

    if args.skip_detection:
        boxes_csv = args.boxes_csv or os.path.join(in_dir, f"{stem}_legende.csv")
        if not os.path.exists(boxes_csv):
            print(f"Fehler: --skip-detection benötigt eine Boxes-CSV (angegeben oder {boxes_csv}).", file=sys.stderr)
            sys.exit(2)
        faces = read_boxes_csv(boxes_csv)
        rects = [(f.x,f.y,f.w,f.h) for f in faces]
        rects = reorder_rects(rects, args.force_single_row, args.row_tol)
        faces = [Face(int(x),int(y),int(w),int(h),id=i+1,name=faces[i].name if i < len(faces) else "") for i,(x,y,w,h) in enumerate(rects)]
    else:
        auto_faces = detect_faces(
            img,
            cascade_path=args.face_cascade,
            scale_factor=args.scale_factor,
            min_neighbors=args.min_neighbors,
            min_size=args.min_size,
            padding=args.padding,
        )
        if not auto_faces:
            print("Hinweis: Automatik fand keine Gesichter – du kannst sie jetzt manuell einzeichnen.")
        rects = [(f.x,f.y,f.w,f.h) for f in auto_faces]
        rects, final_single = edit_boxes_gui(img, rects, args.force_single_row, args.row_tol, font_scale=args.font_scale, font_thickness=args.font_thickness)
        rects = reorder_rects(rects, final_single, args.row_tol)
        faces = [Face(int(x),int(y),int(w),int(h),id=i+1) for i,(x,y,w,h) in enumerate(rects)]

    id2name: Dict[int, str] = {}
    if args.names_csv:
        try:
            id2name = read_names_csv(args.names_csv)
        except Exception as ex:
            print(f"Warnung: Konnte names-csv nicht lesen: {ex}", file=sys.stderr)
    for f in faces:
        if f.id in id2name and id2name[f.id]:
            f.name = id2name[f.id]
    if args.prompt_names:
        prompt_names_in_terminal(faces)
    # Automatisch GUI für Namen öffnen (sofern nicht deaktiviert)
    if not getattr(args, "no_names_gui", False):
        # out_stem vorbereiten
        in_dir, in_name = os.path.split(args.image)
        if not in_dir:
            in_dir = os.getcwd()
        out_dir = args.outdir if args.outdir else in_dir
        os.makedirs(out_dir, exist_ok=True)
        stem, _ = os.path.splitext(in_name)
        out_stem = os.path.join(out_dir, stem)
        # Label-Mode sicher bestimmen
        label_mode = getattr(args, "label_mode", "both")
        try:
            names_gui_edit(faces, out_stem, img, label_mode, args)
        except Exception as ex:
            print(f"Warnung: Konnte das Namens-Frontend nicht öffnen: {ex}", file=sys.stderr)

    label_mode = args.label_mode
    if getattr(args, "no_names_on_image", False) and label_mode == "both":
        label_mode = "number"

    anno = draw_annotations(img, faces, label_mode=label_mode, font_scale=args.font_scale, font_thickness=args.font_thickness, badge_pad=args.badge_pad, badge_shape=args.badge_shape)
    anno_path = f"{out_stem}_nummeriert.jpg"
    cv2.imwrite(anno_path, anno, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

    csv_path, txt_path = save_csv_and_txt(out_stem, faces)

    legend_appended_path = ""
    if args.append_legend:
        entries = [(f.id, f.name) for f in faces]
        strip = build_legend_image(entries, width=anno.shape[1], strip_height=args.legend_strip_height, line_height=args.legend_line_height, col_gap=args.legend_col_gap, col_width=args.legend_col_width, title_scale=args.legend_title_scale, font_scale=args.legend_font_scale, thickness=args.legend_thickness)
        combined = append_strip_to_image(anno, strip)
        legend_appended_path = f"{out_stem}_mit_legende.jpg"
        cv2.imwrite(legend_appended_path, combined, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

    if args.show:
        win = "Ergebnis (Esc zum Schließen)"
        cv2.imshow(win, anno if not legend_appended_path else combined)
        key = cv2.waitKey(0)
        if key == 27:
            cv2.destroyAllWindows()

    print("\\nFertig.")
    print(f"Annotiertes Bild: {anno_path}")
    if legend_appended_path:
        print(f"Bild mit Legendenleiste: {legend_appended_path}")
    print(f"CSV: {csv_path}")
    print(f"TXT: {txt_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\nAbgebrochen.", file=sys.stderr)
        sys.exit(130)
