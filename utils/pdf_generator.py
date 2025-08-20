from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Frame, PageTemplate, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus.flowables import HRFlowable
from io import BytesIO

# --- Custom Page Template with Header and Footer ---
class ProfessionalPageTemplate(PageTemplate):
    def __init__(self, id, pagesize=letter):
        self.pagesize = pagesize
        frame = Frame(inch, inch, pagesize[0] - 2 * inch, pagesize[1] - 2 * inch, id='normal')
        PageTemplate.__init__(self, id=id, frames=[frame])

    def beforeDrawPage(self, canvas, doc):
        # Header
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 16)
        canvas.setFillColor(colors.HexColor('#216d33'))
        canvas.drawString(inch, doc.pagesize[1] - 0.5 * inch, "A/B Test Product Requirements Document")
        canvas.line(inch, doc.pagesize[1] - 0.65 * inch, doc.pagesize[0] - inch, doc.pagesize[1] - 0.65 * inch)
        canvas.restoreState()

        # Footer
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.drawString(inch, 0.5 * inch, f"Page {doc.page}")
        canvas.restoreState()

def create_pdf(prd):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=inch * 1.5, bottomMargin=inch)
    
    # Add the custom page template
    doc.addPageTemplates([ProfessionalPageTemplate('main_template')])

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='H1', fontSize=24, spaceAfter=18, textColor=colors.HexColor('#216d33')))
    styles.add(ParagraphStyle(name='H2', fontSize=16, spaceAfter=12, textColor=colors.black))
    styles.add(ParagraphStyle(name='H3', fontSize=12, spaceAfter=6, textColor=colors.darkslategray))
    styles.add(ParagraphStyle(name='Body', fontSize=10, leading=14, textColor=colors.black))
    
    elements = []
    
    # Horizontal Line Style
    hr = HRFlowable(width="100%", thickness=1, color=colors.lightgrey, spaceBefore=10, spaceAfter=10)

    # --- Introduction ---
    intro = prd.get("intro_data", {})
    elements.append(Paragraph("Introduction", styles['H2']))
    elements.append(Paragraph(f"<b>Business Goal:</b> {intro.get('business_goal', 'N/A')}", styles['Body']))
    elements.append(Paragraph(f"<b>Product Area:</b> {intro.get('product_area', 'N/A')}", styles['Body']))
    elements.append(Paragraph(f"<b>Key Metric:</b> {intro.get('key_metric', 'N/A')} ({intro.get('metric_type', 'N/A')})", styles['Body']))
    elements.append(Paragraph(f"<b>Current Value:</b> {str(intro.get('current_value', 'N/A'))}", styles['Body']))
    elements.append(Paragraph(f"<b>Target Value:</b> {str(intro.get('target_value', 'N/A'))}", styles['Body']))
    elements.append(hr)

    # --- Hypothesis ---
    hyp = prd.get("hypothesis", {})
    elements.append(Paragraph("Hypothesis", styles['H2']))
    elements.append(Paragraph(f"<b>Statement:</b> {hyp.get('Statement', 'N/A')}", styles['Body']))
    elements.append(Paragraph(f"<b>Rationale:</b> {hyp.get('Rationale', 'N/A')}", styles['Body']))
    elements.append(Paragraph(f"<b>Behavioral Basis:</b> {hyp.get('Behavioral Basis', 'N/A')}", styles['Body']))
    elements.append(hr)

    # --- PRD Sections ---
    prd_sections = prd.get("prd_sections", {})
    elements.append(Paragraph("PRD Sections", styles['H2']))
    
    ordered_keys = ["Problem_Statement", "Goal_and_Success_Metrics", "Implementation_Plan"]
    for key in ordered_keys:
        if key in prd_sections:
            content = prd_sections[key]
            display_label = key.replace("_", " ").title()
            elements.append(Paragraph(display_label, styles['H3']))
            if isinstance(content, list):
                for item in content:
                    elements.append(Paragraph(f"• {item}", styles['Body']))
            else:
                elements.append(Paragraph(content, styles['Body']))
            elements.append(Spacer(1, 0.15 * inch))
    elements.append(hr)

    # --- Experiment Plan ---
    calc = prd.get("calculations", {})
    elements.append(Paragraph("Experiment Plan", styles['H2']))
    confidence = f"{round(calc.get('confidence', 0)*100)}%"
    power = f"{round(calc.get('power', 0)*100)}%"
    sample_size = calc.get('sample_size', 'N/A')
    sample_size_str = f"{sample_size:,}" if isinstance(sample_size, int) else "N/A"
    mde = f"{calc.get('min_detectable_effect', 'N/A')}%"
    target_value = str(intro.get('target_value', 'N/A'))
    
    elements.append(Paragraph(f"<b>Confidence Level:</b> {confidence}", styles['Body']))
    elements.append(Paragraph(f"<b>Power Level:</b> {power}", styles['Body']))
    elements.append(Paragraph(f"<b>Minimum Detectable Effect:</b> {mde}", styles['Body']))
    elements.append(Paragraph(f"<b>Target Value:</b> {target_value}", styles['Body']))
    elements.append(Paragraph(f"<b>Sample Size (per variant):</b> {sample_size_str}", styles['Body']))
    elements.append(Paragraph(f"<b>Duration:</b> {calc.get('duration', 'N/A')} days", styles['Body']))
    elements.append(hr)

    # --- Risks & Next Steps ---
    risks = prd.get("risks", [])
    if risks:
        elements.append(Paragraph("Risks & Next Steps", styles['H2']))
        for r in risks:
            elements.append(Paragraph(f"<b>Risk:</b> {r.get('risk', 'N/A')}", styles['Body']))
            elements.append(Paragraph(f"<b>Mitigation:</b> {r.get('mitigation', 'N/A')}", styles['Body']))
            elements.append(Spacer(1, 0.15 * inch))

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
