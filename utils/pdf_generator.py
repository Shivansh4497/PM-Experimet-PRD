from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def create_pdf(prd_data: dict) -> bytes:
    """
    Generates a PDF from the A/B testing PRD data.

    This function uses the reportlab library to create a professional-looking PDF
    document from the structured PRD data. It formats the content with titles,
    sections, and body text.

    Args:
        prd_data (dict): A dictionary containing all the PRD sections and data.

    Returns:
        bytes: The bytes of the generated PDF file.
    """
    # Create a buffer to store the PDF
    from io import BytesIO
    buffer = BytesIO()

    # Create a document object
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Create a list to hold the flowable content for the PDF
    story = []
    
    # Get standard paragraph styles
    styles = getSampleStyleSheet()
    
    # Define custom styles for headers
    styles.add(ParagraphStyle(name='Heading1', fontSize=18, spaceAfter=12, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='Heading2', fontSize=14, spaceAfter=10, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='BodyText', fontSize=10, spaceAfter=6))

    # --- Add PRD Content to the PDF ---
    
    # Title
    story.append(Paragraph("A/B Testing Product Requirements Document", styles['Heading1']))
    story.append(Spacer(1, 0.2 * inch))

    # 1.0 Introduction
    story.append(Paragraph("1.0 Introduction", styles['Heading1']))
    story.append(Paragraph(f"**Business Goal:** {prd_data['intro_data'].get('business_goal', 'N/A')}", styles['BodyText']))
    story.append(Paragraph(f"**Key Metric:** {prd_data['intro_data'].get('key_metric', 'N/A')}", styles['BodyText']))
    story.append(Paragraph(f"**Current Value:** {prd_data['intro_data'].get('current_value', 'N/A')}%", styles['BodyText']))
    story.append(Paragraph(f"**Target Value:** {prd_data['intro_data'].get('target_value', 'N/A')}%", styles['BodyText']))
    story.append(Paragraph(f"**Daily Active Users (DAU):** {prd_data['intro_data'].get('dau', 'N/A')}", styles['BodyText']))
    story.append(Spacer(1, 0.2 * inch))

    # 2.0 Hypothesis
    story.append(Paragraph("2.0 Hypothesis", styles['Heading1']))
    hypothesis = prd_data.get('hypothesis', {})
    story.append(Paragraph(f"**Hypothesis Statement:** {hypothesis.get('Statement', 'N/A')}", styles['BodyText']))
    story.append(Paragraph(f"**Rationale:** {hypothesis.get('Rationale', 'N/A')}", styles['BodyText']))
    story.append(Paragraph(f"**Behavioral Basis:** {hypothesis.get('Behavioral Basis', 'N/A')}", styles['BodyText']))
    story.append(Paragraph(f"**Implementation Steps:** {hypothesis.get('Implementation Steps', 'N/A')}", styles['BodyText']))
    story.append(Spacer(1, 0.2 * inch))

    # 3.0 PRD Sections
    story.append(Paragraph("3.0 PRD Sections", styles['Heading1']))
    prd_sections = prd_data.get('prd_sections', {})
    for section_title, content in prd_sections.items():
        story.append(Paragraph(f"**{section_title}**", styles['Heading2']))
        story.append(Paragraph(content, styles['BodyText']))
    story.append(Spacer(1, 0.2 * inch))

    # 4.0 Experiment Plan
    story.append(Paragraph("4.0 Experiment Plan", styles['Heading1']))
    calculations = prd_data.get('calculations', {})
    story.append(Paragraph(f"**Confidence Level:** {calculations.get('confidence', 'N/A')}", styles['BodyText']))
    story.append(Paragraph(f"**Power Level:** {calculations.get('power', 'N/A')}", styles['BodyText']))
    story.append(Paragraph(f"**Sample Size (per variant):** {calculations.get('sample_size', 'N/A')}", styles['BodyText']))
    story.append(Paragraph(f"**Duration:** {calculations.get('duration', 'N/A')} days", styles['BodyText']))
    story.append(Spacer(1, 0.2 * inch))

    # Build the PDF
    doc.build(story)

    # Move the buffer's cursor to the beginning
    buffer.seek(0)
    
    # Return the byte stream
    return buffer.getvalue()
