from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import os

# Carpeta para guardar los PDFs
PDF_DIR = "static/pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

def generar_pdf_historia(historia_id: int, data: dict):
    """
    Genera un PDF profesional para una historia clínica.
    'data' debe contener: paciente_nombre, paciente_doc, diagnostico, tratamiento, fecha, medico_nombre.
    """
    filename = f"historia_{historia_id}.pdf"
    filepath = os.path.join(PDF_DIR, filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Estilos personalizados
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontSize=18, alignment=1, spaceAfter=20, textColor=colors.HexColor("#2c3e50")
    )
    label_style = ParagraphStyle('LabelStyle', parent=styles['Normal'], fontSize=10, textColor=colors.grey, spaceAfter=2)
    value_style = ParagraphStyle('ValueStyle', parent=styles['Normal'], fontSize=11, spaceAfter=10)

    # Encabezado
    elements.append(Paragraph("MedConnectCo - Historia Clínica Digital", title_style))
    elements.append(Paragraph(f"Referencia: EHR-2026-{historia_id:05d}", styles['Normal']))
    elements.append(Spacer(1, 0.2 * inch))

    # Información del Paciente
    elements.append(Paragraph("<b>INFORMACIÓN DEL PACIENTE</b>", styles['Heading2']))
    elements.append(Spacer(1, 0.1 * inch))
    
    p_data = [
        ["Nombre Completo:", data.get('paciente_nombre', 'N/A')],
        ["Documento:", data.get('paciente_doc', 'N/A')],
        ["Fecha de Registro:", data.get('fecha', 'N/A')]
    ]
    t = Table(p_data, colWidths=[1.5 * inch, 4 * inch])
    t.setStyle(TableStyle([('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'), ('BOTTOMPADDING', (0,0), (-1,-1), 8)]))
    elements.append(t)
    elements.append(Spacer(1, 0.3 * inch))

    # Diagnóstico y Tratamiento
    elements.append(Paragraph("<b>HALLAZGOS CLÍNICOS</b>", styles['Heading2']))
    elements.append(Paragraph("Diagnóstico:", label_style))
    elements.append(Paragraph(data.get('diagnostico', ''), value_style))
    
    elements.append(Paragraph("Plan de Tratamiento:", label_style))
    elements.append(Paragraph(data.get('tratamiento', ''), value_style))
    elements.append(Spacer(1, 0.5 * inch))

    # Firma
    elements.append(Spacer(1, 1 * inch))
    elements.append(Paragraph("___________________________", styles['Normal']))
    elements.append(Paragraph(f"Dr/a. {data.get('medico_nombre', 'ID ' + str(data.get('medico_id')))}", styles['Normal']))
    elements.append(Paragraph("Firma y Sello Médico Autorizado", label_style))

    # Pie de página (se define en el build del doc)
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.drawString(inch, 0.75 * inch, "MedConnectCo — Red Nacional de Historias Clínicas · Colombia")
        canvas.drawRightString(7.5 * inch, 0.75 * inch, f"Página {doc.page}")
        canvas.restoreState()

    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    return filename
