from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def generate_report(
    filename,
    name,
    email,
    phone,
    score,
    ats_score,
    skills,
    suggestions
):
    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    content = []

    content.append(
        Paragraph("Resume Analysis Report", styles["Title"])
    )

    content.append(Spacer(1, 12))

    content.append(
        Paragraph(f"<b>Name:</b> {name}", styles["Normal"])
    )

    content.append(
        Paragraph(f"<b>Email:</b> {email}", styles["Normal"])
    )

    content.append(
        Paragraph(f"<b>Phone:</b> {phone}", styles["Normal"])
    )

    content.append(Spacer(1, 12))

    content.append(
        Paragraph(f"<b>Resume Score:</b> {score}/100", styles["Normal"])
    )

    content.append(
        Paragraph(f"<b>ATS Score:</b> {ats_score}/100", styles["Normal"])
    )

    content.append(
        Paragraph(
            f"<b>Skills:</b> {', '.join(skills)}",
            styles["Normal"]
        )
    )

    content.append(Spacer(1, 12))

    content.append(
        Paragraph("<b>Suggestions:</b>", styles["Heading2"])
    )

    for suggestion in suggestions:
        content.append(
            Paragraph(f"• {suggestion}", styles["Normal"])
        )

    doc.build(content)