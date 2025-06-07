from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from record_system import get_letter_grade

def generate_marksheet_pdf(name, roll_no, grades, gpa, status, file_path):
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # Margins and Layout
    margin = 40
    line_height = 18
    y_cursor = height - margin

    # Draw outer border
    c.setStrokeColor(colors.darkblue)
    c.setLineWidth(2)
    c.rect(margin, margin, width - 2 * margin, height - 2 * margin)

    # Logo (optional)
    logo_path = "static/logo.png"
    try:
        c.drawImage(logo_path, width / 2 - 40, y_cursor - 60, width=80, preserveAspectRatio=True, mask='auto')
    except:
        pass

    # Header
    y_cursor -= 80
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2, y_cursor, "Woxsen University")
    y_cursor -= 25
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, y_cursor, "Academic Record Marksheet")

    # Student Info Box
    y_cursor -= 50
    info_box_height = 80
    c.setStrokeColor(colors.grey)
    c.setFillColor(colors.whitesmoke)
    c.rect(margin + 10, y_cursor - info_box_height + 10, width - 2 * margin - 20, info_box_height, fill=1)

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)
    info_y = y_cursor
    info_x = margin + 20

    c.drawString(info_x, info_y, f"Name: {name.title()}")
    c.drawString(info_x, info_y - line_height, f"Roll No: {roll_no}")
    c.drawString(info_x, info_y - 2 * line_height, f"Status: {status}")
    c.drawString(info_x, info_y - 3 * line_height, f"GPA: {gpa:.2f}")

    # Grades Table Header
    y_cursor -= info_box_height + 30
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.lightgrey)
    c.rect(margin + 10, y_cursor, width - 2 * margin - 20, 22, fill=1, stroke=0)

    c.setFillColor(colors.black)
    c.drawString(margin + 15, y_cursor + 5, "Subject")
    c.drawString(margin + 200, y_cursor + 5, "IA1")
    c.drawString(margin + 250, y_cursor + 5, "IA2")
    c.drawString(margin + 300, y_cursor + 5, "Final")
    c.drawString(margin + 370, y_cursor + 5, "Grade")

    y_cursor -= 25

    # Grades Table Rows
    c.setFont("Helvetica", 11)
    for subject, scores in grades.items():
        total = (scores["IA1"] * 0.25 + scores["IA2"] * 0.25 + scores["Final"] * 0.50)
        grade = get_letter_grade(total)
        c.setFillColor(colors.white if (y_cursor // 20) % 2 == 0 else colors.lightgrey)
        c.rect(margin + 10, y_cursor, width - 2 * margin - 20, 20, fill=1, stroke=0)

        c.setFillColor(colors.black)
        c.drawString(margin + 15, y_cursor + 5, subject)
        c.drawString(margin + 200, y_cursor + 5, str(scores["IA1"]))
        c.drawString(margin + 250, y_cursor + 5, str(scores["IA2"]))
        c.drawString(margin + 300, y_cursor + 5, str(scores["Final"]))
        c.drawString(margin + 370, y_cursor + 5, grade)
        y_cursor -= 20

        if y_cursor < margin + 120:
            c.showPage()
            y_cursor = height - margin

    # Signature
    y_cursor -= 40
    c.setFont("Helvetica", 12)
    c.drawString(margin + 20, y_cursor, "Signature (Academic Officer):")
    c.line(margin + 200, y_cursor, margin + 400, y_cursor)

    y_cursor -= 30
    c.drawString(margin + 20, y_cursor, "Date of Issue:")
    c.line(margin + 200, y_cursor, margin + 400, y_cursor)

    # Footer
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors.grey)
    c.drawRightString(width - margin, margin - 10, "Generated using ReportLab | Woxsen Academic Portal")

    c.save()
