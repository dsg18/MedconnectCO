"""
pdf_service.py — Generación de PDFs de historias clínicas.
"""
import os
import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable,
)

# Carpeta donde se guardan los PDFs
PDFS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pdfs")
os.makedirs(PDFS_DIR, exist_ok=True)

# Paleta de colores médica
AZUL       = colors.HexColor("#1e3a5f")
AZUL_LIGHT = colors.HexColor("#4a6fa5")
GRIS       = colors.HexColor("#6b7280")
FONDO1     = colors.HexColor("#f0f4ff")
FONDO2     = colors.HexColor("#e8eeff")
BORDE      = colors.HexColor("#c0cadf")


def generar_pdf_historia(
    historia_id: int,
    paciente_doc: str,
    paciente_nombre: str,
    medico_username: str,
    hospital_nombre: str,
    diagnostico: str,
    tratamiento: str,
    fecha: datetime.datetime,
) -> str:
    """
    Genera el PDF de la historia clínica y retorna la ruta absoluta del archivo.
    """
    filename = f"historia_{historia_id}.pdf"
    filepath = os.path.join(PDFS_DIR, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm,
        topMargin=2 * cm,   bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    def style(name, **kwargs):
        return ParagraphStyle(name, parent=styles["Normal"], **kwargs)

    S = {
        "titulo":    style("T", fontSize=16, textColor=AZUL, alignment=TA_CENTER, spaceAfter=4, fontName="Helvetica-Bold"),
        "subtitulo": style("S", fontSize=10, textColor=AZUL_LIGHT, alignment=TA_CENTER, spaceAfter=2),
        "seccion":   style("Se", fontSize=12, textColor=AZUL, fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=4),
        "cuerpo":    style("C", fontSize=11, leading=16, spaceAfter=6),
        "pie":       style("P", fontSize=8, textColor=GRIS, alignment=TA_CENTER),
        "firma_lab": style("FL", fontSize=9, textColor=AZUL_LIGHT, alignment=TA_CENTER, fontName="Helvetica-Bold"),
        "firma_val": style("FV", fontSize=9, textColor=GRIS, alignment=TA_CENTER),
    }

    fecha_str = fecha.strftime("%d/%m/%Y  %H:%M") if isinstance(fecha, datetime.datetime) else str(fecha)

    elems = []

    # ── Encabezado ────────────────────────────────────────────────────────────
    elems.append(Paragraph("MEDCONNECTCO", S["titulo"]))
    elems.append(Paragraph("Sistema Nacional de Salud · Colombia", S["subtitulo"]))
    if hospital_nombre:
        elems.append(Paragraph(hospital_nombre, S["subtitulo"]))
    elems.append(Spacer(1, 0.3 * cm))
    elems.append(HRFlowable(width="100%", thickness=2, color=AZUL))
    elems.append(Spacer(1, 0.4 * cm))

    elems.append(Paragraph("HISTORIA CLÍNICA / ORDEN MÉDICA", style(
        "DocT", fontSize=14, alignment=TA_CENTER, textColor=AZUL,
        fontName="Helvetica-Bold", spaceAfter=12,
    )))

    # ── Tabla de datos básicos ────────────────────────────────────────────────
    info = [
        ["N° Historia:",        f"#{historia_id}",         "Fecha:",              fecha_str],
        ["Médico tratante:",    medico_username,            "Documento paciente:", paciente_doc],
        ["Nombre del paciente:", paciente_nombre or "—",   "",                    ""],
    ]

    t_info = Table(info, colWidths=[4 * cm, 6 * cm, 4 * cm, 4 * cm])
    t_info.setStyle(TableStyle([
        ("FONTNAME",   (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME",   (0, 0), (0, -1),  "Helvetica-Bold"),
        ("FONTNAME",   (2, 0), (2, -1),  "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 10),
        ("TEXTCOLOR",  (0, 0), (0, -1),  AZUL_LIGHT),
        ("TEXTCOLOR",  (2, 0), (2, -1),  AZUL_LIGHT),
        ("BACKGROUND", (0, 0), (-1, 0),  FONDO1),
        ("BACKGROUND", (0, 1), (-1, 1),  FONDO2),
        ("BACKGROUND", (0, 2), (-1, 2),  FONDO1),
        ("GRID",       (0, 0), (-1, -1), 0.5, BORDE),
        ("PADDING",    (0, 0), (-1, -1), 8),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("SPAN",       (1, 2), (3, 2)),
    ]))
    elems.append(t_info)
    elems.append(Spacer(1, 0.5 * cm))
    elems.append(HRFlowable(width="100%", thickness=1, color=BORDE))

    # ── Diagnóstico ───────────────────────────────────────────────────────────
    elems.append(Paragraph("DIAGNÓSTICO", S["seccion"]))
    for linea in diagnostico.split("\n"):
        elems.append(Paragraph(linea.strip() or "&nbsp;", S["cuerpo"]))
    elems.append(Spacer(1, 0.3 * cm))

    # ── Tratamiento ───────────────────────────────────────────────────────────
    elems.append(HRFlowable(width="100%", thickness=1, color=BORDE))
    elems.append(Paragraph("TRATAMIENTO / PRESCRIPCIÓN", S["seccion"]))
    for linea in tratamiento.split("\n"):
        elems.append(Paragraph(linea.strip() or "&nbsp;", S["cuerpo"]))
    elems.append(Spacer(1, 1.2 * cm))

    # ── Bloque de firmas ──────────────────────────────────────────────────────
    elems.append(HRFlowable(width="100%", thickness=1, color=BORDE))
    elems.append(Spacer(1, 0.5 * cm))

    firmas = [
        ["_" * 30, "", "_" * 30],
        ["Firma del Médico", "", "Sello / Firma del Hospital"],
        [medico_username, "", hospital_nombre or ""],
    ]
    t_firmas = Table(firmas, colWidths=[7 * cm, 3.5 * cm, 7 * cm])
    t_firmas.setStyle(TableStyle([
        ("ALIGNMENT",  (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("TEXTCOLOR",  (0, 1), (-1, 1),  AZUL_LIGHT),
        ("FONTNAME",   (0, 1), (-1, 1),  "Helvetica-Bold"),
        ("TEXTCOLOR",  (0, 2), (-1, 2),  GRIS),
    ]))
    elems.append(t_firmas)

    # ── Pie de página ─────────────────────────────────────────────────────────
    elems.append(Spacer(1, 0.6 * cm))
    elems.append(HRFlowable(width="100%", thickness=0.5, color=BORDE))
    elems.append(Spacer(1, 0.2 * cm))
    pie = (
        f"Documento generado el {datetime.datetime.now().strftime('%d/%m/%Y a las %H:%M')} "
        "· MedConnectCo · Colombia"
    )
    elems.append(Paragraph(pie, S["pie"]))

    doc.build(elems)
    return filepath
