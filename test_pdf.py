from fpdf import FPDF
import os

pdf = FPDF()
pdf.add_page()
font_path = 'utils/NotoSansGujarati-Regular.ttf'

print(f"Testing font: {font_path}")
print(f"File exists: {os.path.exists(font_path)}")

try:
    pdf.add_font('Gujarati', '', font_path)
    pdf.set_font('Gujarati', '', 14)
    pdf.cell(10, 10, "Hello World")
    print("Font added successfully.")
    
    # Try adding Gujarati text
    text = "નમસ્તે"
    pdf.cell(10, 10, text)
    print("Gujarati text added.")
    
    out = pdf.output()
    print(f"Output generated. Size: {len(out)} bytes")
except Exception as e:
    print(f"ERROR: {e}")
