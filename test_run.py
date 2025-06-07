import streamlit as st
from reportlab.pdfgen import canvas
import tempfile

def generate_dummy_pdf(path):
    c = canvas.Canvas(path)
    c.drawString(100, 750, "This is a test PDF!")
    c.save()

st.title("PDF Download Test")

if st.button("📄 Generate PDF"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        generate_dummy_pdf(tmp.name)
        with open(tmp.name, "rb") as f:
            st.download_button(
                label="⬇️ Download PDF",
                data=f.read(),
                file_name="test_output.pdf",
                mime="application/pdf"
            )