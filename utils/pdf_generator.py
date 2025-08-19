from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from io import BytesIO

def create_pdf(prd):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=14
    )
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10
    )
    normal_style = styles['Normal']

    # --- Intro ---
    intro = prd.get("intro_data", {})
    metric_unit = intro.get("metric_unit", "")
    if metric_unit:  
        metric_unit = f" {metric_unit}"  # add space before unit if exists

    elements.append(Paragraph("A/B Testing PRD", title_style))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("1.0 Introduction", section_style))
    elements.append(Paragraph(f"Business Goal: {intro.get('business_goal', 'N/A')}", normal_style))
    elements.append(Paragraph(f"Product Area: {intro.get('product_area', 'N/A')}", normal_style))
    elements.append(Paragraph(f"Product Type: {intro.get('product_type', 'N/A')}", normal_style))
    elements.append(Paragraph(f"Key Metric: {intro.get('key_metric', 'N/A')}", normal_style))
    elements.append(Paragraph(f"Current Value: {intro.get('current_value', 'N/A')}{metric_unit}", normal_style))
    elements.append(Paragraph(f"Target Value: {intro.get('target_value', 'N/A')}{metric_unit}", normal_style))
    elements.append(Paragraph(f"Daily Active Users (DAU): {intro.get('dau', 'N/A')}", normal_style))
    elements.append(Spacer(1, 12))

    # --- Hypothesis ---
    hyp = prd.get("hypothesis", {})
    elements.append(Paragraph("2.0 Hypothesis", section_style))
    elements.append(Paragraph(f"Statement: {hyp.get('Statement', 'N/A')}", normal_style))
    elements.append(Paragraph(f"Rationale: {hyp.get('Rationale', 'N/A')}", normal_style))
    elements.append(Paragraph(f"Behavioral Basis: {hyp.get('Behavioral Basis', 'N/A')}", normal_style))
    elements.append(Paragraph(f"Implementation Steps: {hyp.get('Implementation Steps', 'N/A')}", normal_style))
    elements.append(Spacer(1, 12))

    # --- PRD Sections ---
    prd_sections = prd.get("prd_sections", {})
    elements.append(Paragraph("3.0 PRD Sections", section_style))
    for section_title, content in prd_sections.items():
        elements.append(Paragraph(section_title, section_style))
        if isinstance(content, str):
            elements.append(Paragraph(content, normal_style))
        elif isinstance(content, list):
            for item in content:
                elements.append(Paragraph(f"- {item}", normal_style))
        elif isinstance(content, dict):
            for k, v in content.items():
                elements.append(Paragraph(f"{k}: {v}", normal_style))
        elements.append(Spacer(1, 8))

    # --- Experiment Plan ---
    calc = prd.get("calculations", {})
    elements.append(Paragraph("4.0 Experiment Plan", section_style))
    confidence = calc.get("confidence", "N/A")
    power = calc.get("power", "N/A")

    # Convert floats (0.95 → 95%) 
    if isinstance(confidence, float):
        confidence = f"{round(confidence*100)}%"
    if isinstance(power, float):
        power = f"{round(power*100)}%"

    elements.append(Paragraph(f"Confidence Level: {confidence}", normal_style))
    elements.append(Paragraph(f"Power Level: {power}", normal_style))
    elements.append(Paragraph(f"Sample Size (per variant): {calc.get('sample_size', 'N/A')}", normal_style))
    elements.append(Paragraph(f"Duration: {calc.get('duration', 'N/A')} days", normal_style))

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
