from fpdf import FPDF
import datetime
import os
from io import BytesIO

class FarmReport(FPDF):
    def __init__(self, lang_code='en', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lang_code = lang_code
        self.font_reg = os.path.join(os.path.dirname(__file__), 'NotoSansGujarati-Regular.ttf')
        self.font_bold = os.path.join(os.path.dirname(__file__), 'NotoSansGujarati-Bold.ttf')
        
        # Add Gujarati font if it exists
        if os.path.exists(self.font_reg):
            self.add_font('Gujarati', '', self.font_reg)
            self.add_font('Gujarati', 'I', self.font_reg) # Fallback Italic to Regular
            if os.path.exists(self.font_bold):
                self.add_font('Gujarati', 'B', self.font_bold)
                self.add_font('Gujarati', 'BI', self.font_bold) # Fallback Bold-Italic to Bold
            else:
                self.add_font('Gujarati', 'B', self.font_reg)
            self.custom_font = 'Gujarati'
        else:
            self.custom_font = 'Arial'

    def header(self):
        # Set font
        self.set_font(self.custom_font if self.lang_code == 'gu' else 'Arial', 'B', 15)
        
        # Title
        title = 'Krishi-Mitra AI: Farm Status Report'
        if self.lang_code == 'gu':
            title = 'કૃષિ-મિત્ર AI: ખેતર સ્થિતિ રિપોર્ટ'
            
        self.cell(0, 10, title, 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.custom_font if self.lang_code == 'gu' else 'Arial', 'I', 8)
        
        page_label = 'Page' if self.lang_code == 'en' else 'પાનું'
        self.cell(0, 10, f'{page_label} ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

def generate_farm_report(user_name, user_email, city, size, active_crops, live_data=None, lang_code='en', t=None):
    """
    Generate a PDF report for the user's farm supporting multiple languages.
    """
    if t is None: t = {}

    pdf = FarmReport(lang_code=lang_code)
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # helper for localized text
    def put_text(text, font_size=10, style='', ln=1, align='L', fill=0):
        # Determine if text has Gujarati characters
        has_gujarati = any('\u0a80' <= c <= '\u0aff' for c in text)
        font = pdf.custom_font if (has_gujarati or lang_code == 'gu') else 'Arial'
        pdf.set_font(font, style, font_size)
        pdf.cell(0, 7 if ln else 0, text, 0, ln, align, fill)

    # User Profile Section
    put_text(t.get('farm_profile_label', 'Farm Profile'), font_size=12, style='B')
    
    lbl_name = 'Farmer Name' if lang_code == 'en' else 'ખેડૂતનું નામ'
    lbl_email = 'Email' if lang_code == 'en' else 'ઇમેઇલ'
    lbl_loc = t.get('location', 'Location')
    lbl_size = t.get('farm_size', 'Farm Size')
    lbl_gen = 'Generated On' if lang_code == 'en' else 'રિપોર્ટ તારીખ'
    
    put_text(f"{lbl_name}: {user_name}", font_size=10)
    put_text(f"{lbl_email}: {user_email}", font_size=10)
    put_text(f"{lbl_loc}: {city}", font_size=10)
    put_text(f"{lbl_size}: {size} Acres", font_size=10)
    put_text(f"{lbl_gen}: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", font_size=10)
    pdf.ln(5)
    
    # Live Environment Section
    if live_data:
        put_text(t.get('micro_climate', 'Micro-Climate'), font_size=12, style='B')
        
        w = live_data.get('weather', {})
        s = live_data.get('soil', {})
        
        lbl_temp = t.get('temperature', 'Temperature')
        lbl_hum = t.get('humidity', 'Humidity')
        lbl_soil_m = t.get('soil_moisture', 'Soil Moisture')
        lbl_soil_t = t.get('soil_temp', 'Soil Temp')
        
        # Avoid ° symbol to eliminate encoding issues, use "C" or "Celsius"
        temp_val = f"{w.get('temp', '--')} C"
        soil_temp_val = f"{s.get('soil_temp', '--')} C"
        
        put_text(f"{lbl_temp}: {temp_val} | {lbl_hum}: {w.get('humidity', '--')}%", font_size=10)
        put_text(f"{lbl_soil_m}: {s.get('moisture', '--')}% | {lbl_soil_t}: {soil_temp_val}", font_size=10)
        pdf.ln(5)

    # Active Crops Section
    put_text(t.get('active_crop_fields', 'Active Crop Fields'), font_size=12, style='B')
    pdf.ln(2)
    
    if not active_crops:
        put_text(t.get('no_crops_added', 'No active crops registered.'), font_size=10, style='I')
    else:
        # Table Header
        header_font = pdf.custom_font if lang_code == 'gu' else 'Arial'
        pdf.set_font(header_font, 'B' if lang_code == 'en' else '', 10)
        pdf.set_fill_color(240, 240, 240)
        
        pdf.cell(50, 8, t.get('crop_name_label', 'Crop Name'), 1, 0, 'C', 1)
        pdf.cell(30, 8, t.get('area_label', 'Area (Ac)'), 1, 0, 'C', 1)
        pdf.cell(35, 8, t.get('planting_date', 'Planting Date'), 1, 0, 'C', 1)
        pdf.cell(35, 8, t.get('chlorophyll', 'Chlorophyll'), 1, 0, 'C', 1)
        pdf.cell(40, 8, 'Health' if lang_code == 'en' else 'સ્વાસ્થ્ય', 1, 1, 'C', 1)
        
        # Table Body
        for crop in active_crops:
            c_name = str(crop['crop_name'])
            # Decide font for each cell
            pdf.set_font(pdf.custom_font if any('\u0a80' <= char <= '\u0aff' for char in c_name) else 'Arial', '', 9)
            pdf.cell(50, 8, c_name, 1, 0, 'C')
            
            pdf.set_font('Arial', '', 9)
            pdf.cell(30, 8, str(crop['area']), 1, 0, 'C')
            pdf.cell(35, 8, str(crop['planting_date']), 1, 0, 'C')
            pdf.cell(35, 8, str(crop.get('chlorophyll', 'N/A')), 1, 0, 'C')
            
            h_status = str(crop.get('health_status', 'N/A'))
            pdf.set_font(pdf.custom_font if any('\u0a80' <= char <= '\u0aff' for char in h_status) else 'Arial', '', 9)
            pdf.cell(40, 8, h_status, 1, 1, 'C')

    # Footer Note
    pdf.ln(10)
    note = "Note: This report is generated by Krishi-Mitra AI. Plant health analysis is based on image processing and current environmental data. For critical farming decisions, please consult with an agricultural expert."
    if lang_code == 'gu':
        note = "નોંધ: આ રિપોર્ટ કૃષિ-મિત્ર AI દ્વારા તૈયાર કરવામાં આવ્યો છે. છોડના સ્વાસ્થ્યનું વિશ્લેષણ ઈમેજ પ્રોસેસિંગ અને વર્તમાન પર્યાવરણીય ડેટા પર આધારિત છે. ખેતીના મહત્વના નિર્ણયો માટે, કૃપા કરીને કૃષિ નિષ્ણાતની સલાહ લો."
    
    pdf.set_font(pdf.custom_font if lang_code == 'gu' else 'Arial', 'I' if lang_code == 'en' else '', 8)
    pdf.multi_cell(0, 5, note)
    
    # Return as clean bytes
    try:
        pdf_output = pdf.output()
        if isinstance(pdf_output, str):
            return pdf_output.encode('latin-1')
        return bytes(pdf_output)
    except Exception as e:
        print(f"PDF Output Error: {e}")
        raise e
