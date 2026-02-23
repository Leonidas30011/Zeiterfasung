import sqlite3
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# PDF (ReportLab)
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Save-Dialog
import tkinter as tk
from tkinter import filedialog, messagebox


DB_PATH = Path("datenbank/Zeiterfassung.db")


def connect_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def parse_dt(s: str) -> datetime:
    # Erwartet ISO-Format: "YYYY-MM-DD HH:MM:SS" (oder ähnlich ISO-kompatibel)
    # datetime.fromisoformat akzeptiert "YYYY-MM-DD HH:MM:SS"
    return datetime.fromisoformat(s)


def seconds_to_hours(sec: int) -> float:
    return sec / 3600.0


def fmt_hours(h: float) -> str:
    # 2 Nachkommastellen, deutsch-friendly mit Komma wäre möglich,
    # aber lassen wir's technisch sauber als Punkt:
    return f"{h:.2f} h"


def fetch_bookings():
    """
    Liefert Liste von Buchungen:
    (person_name, projekt_name, start_dt, end_dt)
    Nur abgeschlossene Buchungen.
    """
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT pe.name, pr.name, b.einstempelzeit, b.ausstempelzeit
        FROM buchungen b
        JOIN personen pe ON pe.id = b.person_id
        JOIN projekte pr ON pr.id = b.projekt_id
        WHERE b.ausstempelzeit IS NOT NULL
        ORDER BY b.einstempelzeit ASC;
    """)
    rows = cur.fetchall()
    conn.close()

    bookings = []
    for person, projekt, start_s, end_s in rows:
        try:
            start_dt = parse_dt(start_s)
            end_dt = parse_dt(end_s)
        except Exception:
            # Falls mal ein Datensatz kaputt ist, skippen
            continue

        if end_dt <= start_dt:
            continue

        bookings.append((person, projekt, start_dt, end_dt))

    return bookings


def build_monthly_aggregates(bookings):
    """
    Monatsschlüssel = "YYYY-MM"
    Regel: zählt immer in den Monat der einstempelzeit (Start).
    """
    # month -> person -> project -> seconds
    per_person = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    # month -> project -> person -> seconds
    per_project = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for person, projekt, start_dt, end_dt in bookings:
        month_key = start_dt.strftime("%Y-%m")  # Vormonat-Regel automatisch erfüllt
        duration_sec = int((end_dt - start_dt).total_seconds())

        per_person[month_key][person][projekt] += duration_sec
        per_project[month_key][projekt][person] += duration_sec

    return per_person, per_project


def make_table(data, col_widths=None):
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def generate_pdf(output_path: Path, per_person, per_project):
    styles = getSampleStyleSheet()
    story = []

    title = "Zeiterfassung – Monatsauswertung"
    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 12))

    created = datetime.now().strftime("%Y-%m-%d %H:%M")
    story.append(Paragraph(f"Erstellt am: {created}", styles["Normal"]))
    story.append(Spacer(1, 16))

    months = sorted(set(per_person.keys()) | set(per_project.keys()))
    if not months:
        story.append(Paragraph("Keine abgeschlossenen Buchungen gefunden.", styles["Normal"]))
        doc = SimpleDocTemplate(str(output_path), pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        doc.build(story)
        return

    for idx, month in enumerate(months):
        story.append(Paragraph(f"Monat: {month}", styles["Heading1"]))
        story.append(Spacer(1, 8))

        # -------------------------
        # Personen-Sektion
        # -------------------------
        story.append(Paragraph("Personen", styles["Heading2"]))
        story.append(Spacer(1, 6))

        persons = sorted(per_person.get(month, {}).keys())
        if not persons:
            story.append(Paragraph("Keine Zeiten für Personen in diesem Monat.", styles["Normal"]))
            story.append(Spacer(1, 10))
        else:
            for person in persons:
                projects_map = per_person[month][person]  # projekt -> sec
                if not projects_map:
                    continue

                story.append(Paragraph(f"{person}", styles["Heading3"]))

                # Tabelle: Projekt | Stunden
                rows = [["Projekt", "Stunden"]]
                total_sec = 0
                for proj in sorted(projects_map.keys()):
                    sec = projects_map[proj]
                    if sec <= 0:
                        continue
                    total_sec += sec
                    rows.append([proj, fmt_hours(seconds_to_hours(sec))])

                # Gesamt
                rows.append(["Gesamt", fmt_hours(seconds_to_hours(total_sec))])

                story.append(make_table(rows, col_widths=[360, 120]))
                story.append(Spacer(1, 12))

        story.append(Spacer(1, 6))

        # -------------------------
        # Projekte-Sektion
        # -------------------------
        story.append(Paragraph("Projekte", styles["Heading2"]))
        story.append(Spacer(1, 6))

        projects = sorted(per_project.get(month, {}).keys())
        if not projects:
            story.append(Paragraph("Keine Zeiten für Projekte in diesem Monat.", styles["Normal"]))
        else:
            for proj in projects:
                persons_map = per_project[month][proj]  # person -> sec
                if not persons_map:
                    continue

                story.append(Paragraph(f"{proj}", styles["Heading3"]))

                rows = [["Person", "Stunden"]]
                total_sec = 0
                for person in sorted(persons_map.keys()):
                    sec = persons_map[person]
                    if sec <= 0:
                        continue
                    total_sec += sec
                    rows.append([person, fmt_hours(seconds_to_hours(sec))])

                rows.append(["Gesamt", fmt_hours(seconds_to_hours(total_sec))])

                story.append(make_table(rows, col_widths=[360, 120]))
                story.append(Spacer(1, 12))

        if idx < len(months) - 1:
            story.append(PageBreak())

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    doc.build(story)


def choose_save_path() -> Path | None:
    root = tk.Tk()
    root.withdraw()
    root.update()

    file_path = filedialog.asksaveasfilename(
        title="PDF speichern unter...",
        defaultextension=".pdf",
        filetypes=[("PDF-Datei", "*.pdf")],
        initialfile="Zeiterfassung_Auswertung.pdf"
    )

    root.destroy()

    if not file_path:
        return None
    return Path(file_path)


def main():
    if not DB_PATH.exists():
        messagebox.showerror("Fehler", f"Datenbank nicht gefunden:\n{DB_PATH}")
        return

    bookings = fetch_bookings()
    per_person, per_project = build_monthly_aggregates(bookings)

    out_path = choose_save_path()
    if out_path is None:
        return

    try:
        generate_pdf(out_path, per_person, per_project)
        messagebox.showinfo("Fertig", f"PDF erstellt:\n{out_path}")
    except Exception as e:
        messagebox.showerror("Fehler", f"PDF konnte nicht erstellt werden:\n{e}")


if __name__ == "__main__":
    main()
