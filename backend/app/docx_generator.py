"""DOCX generation for exam structures."""

import io
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

from app.models import ExamStructure


def generate_exam_docx(exam: ExamStructure) -> bytes:
    """Generate a DOCX file from an ExamStructure and return as bytes."""
    doc = Document()

    # Styles
    style = doc.styles["Normal"]
    style.font.name = "Arial"
    style.font.size = Pt(11)

    # ── Title ──
    title = doc.add_heading(f"Klassenarbeit: {exam.thema}", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # ── Metadata ──
    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta.add_run(f"Fach: {exam.fach}  |  Klasse: {exam.klasse}  |  Dauer: {exam.dauer_minuten} Minuten  |  Gesamtpunkte: {exam.gesamtpunkte}")
    meta.runs[0].font.size = Pt(10)
    meta.runs[0].font.color.rgb = RGBColor(100, 100, 100)

    # ── Hinweise ──
    if exam.hinweise:
        doc.add_heading("Hinweise", level=2)
        for h in exam.hinweise:
            doc.add_paragraph(h, style="List Bullet")

    doc.add_paragraph()  # spacer

    # ── Aufgaben ──
    doc.add_heading("Aufgaben", level=1)
    for i, task in enumerate(exam.aufgaben, 1):
        p = doc.add_paragraph()
        run = p.add_run(f"Aufgabe {i} ")
        run.bold = True
        run.font.size = Pt(12)

        badge = p.add_run(f"[AFB {task.afb_level}] ")
        badge.font.size = Pt(9)
        badge.font.color.rgb = RGBColor(80, 80, 80)

        pts = p.add_run(f"({task.punkte} Punkte)")
        pts.font.size = Pt(10)
        pts.font.color.rgb = RGBColor(120, 120, 120)

        doc.add_paragraph(task.beschreibung)
        doc.add_paragraph()  # spacer

    # ── Page break before Erwartungshorizont ──
    doc.add_page_break()

    # ── Erwartungshorizont ──
    doc.add_heading("Erwartungshorizont", level=1)

    table = doc.add_table(rows=1, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"

    hdr = table.rows[0].cells
    for cell, text in zip(hdr, ["Aufgabe", "AFB", "Erwartete Leistung", "Punkte"]):
        cell.text = text
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True
                run.font.size = Pt(10)

    for i, task in enumerate(exam.aufgaben, 1):
        row = table.add_row().cells
        row[0].text = str(i)
        row[1].text = task.afb_level
        row[2].text = "\n".join(f"• {e}" for e in task.erwartung)
        row[3].text = str(task.punkte)

    doc.add_paragraph()

    # ── Notenschlüssel ──
    doc.add_heading("Bewertungsraster / Notenschlüssel", level=2)

    note_table = doc.add_table(rows=1, cols=2)
    note_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    note_table.style = "Table Grid"

    hdr2 = note_table.rows[0].cells
    hdr2[0].text = "Note"
    hdr2[1].text = "Punkte"
    for cell in hdr2:
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True

    for note, punkte in exam.notenschluessel.items():
        row = note_table.add_row().cells
        row[0].text = note
        row[1].text = punkte

    # ── Write to bytes ──
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
