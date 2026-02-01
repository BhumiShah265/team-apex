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
        self.use_custom_font = False
        
        # Add Gujarati font if it exists
        try:
            if os.path.exists(self.font_reg):
                self.add_font('Gujarati', '', self.font_reg)
                self.add_font('Gujarati', 'I', self.font_reg)
                if os.path.exists(self.font_bold):
                    self.add_font('Gujarati', 'B', self.font_bold)
                    self.add_font('Gujarati', 'BI', self.font_bold)
                else:
                    self.add_font('Gujarati', 'B', self.font_reg)
                self.custom_font = 'Gujarati'
                self.use_custom_font = True
            else:
                self.custom_font = 'Arial'
        except Exception as e:
            print(f"Font loading error: {e}")
            self.custom_font = 'Arial'
            self.use_custom_font = False

    def header(self):
        # Set font
        font_to_use = self.custom_font if (self.lang_code == 'gu' and self.use_custom_font) else 'Arial'
        self.set_font(font_to_use, 'B', 15)
        
        # Title
        title = 'Krishi-Mitra AI: Farm Status Report'
        if self.lang_code == 'gu' and self.use_custom_font:
            title = 'કૃષિ-મિત્ર AI: ખેતર સ્થિતિ રિપોર્ટ'
            
        # Clean title if using Arial
        if font_to_use == 'Arial':
            title = title.encode('latin-1', 'replace').decode('latin-1')
            
        self.cell(0, 10, title, 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        font_to_use = self.custom_font if (self.lang_code == 'gu' and self.use_custom_font) else 'Arial'
        self.set_font(font_to_use, 'I', 8)
        
        page_label = 'Page' if self.lang_code == 'en' else 'પાનું'
        # Check chars
        if font_to_use == 'Arial':
           page_label = 'Page'
           
        self.cell(0, 10, f'{page_label} ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

def generate_farm_report(user_name, user_email, city, size, active_crops, live_data=None, lang_code='en', t=None):
    """
    Generate a PDF report.
    Tries to use Gujarati Unicode font.
    If ANY error occurs, falls back to a Safe Mode (English/Arial) report.
    """
    try:
        return _generate_report_internal(user_name, user_email, city, size, active_crops, live_data, lang_code, t, safe_mode=False)
    except Exception as e:
        print(f"Primary PDF Generation Failed: {e}")
        try:
            # Fallback to Safe Mode
            return _generate_report_internal(user_name, user_email, city, size, active_crops, live_data, lang_code='en', t=t, safe_mode=True)
        except Exception as e2:
             print(f"Safe Mode PDF Generation Failed: {e2}")
             # Return valid empty bytes or minimal error PDF
             pdf = FPDF()
             pdf.add_page()
             pdf.set_font("Arial", "", 12)
             pdf.cell(0, 10, "Error generating report.")
             return bytes(pdf.output())

def _generate_report_internal(user_name, user_email, city, size, active_crops, live_data, lang_code, t, safe_mode=False):
    if t is None: t = {}
    
    # If safe mode, force English and Arial
    if safe_mode:
        lang_code = 'en'

    pdf = FarmReport(lang_code=lang_code)
    # If safe mode, disable custom font usage manually
    if safe_mode:
        pdf.use_custom_font = False
        pdf.custom_font = 'Arial'

    pdf.alias_nb_pages()
    pdf.add_page()
    
    # helper for localized text
    def put_text(text, font_size=10, style='', ln=1, align='L', fill=0):
        if not text: text = ""
        
        # Determine font
        has_gujarati = any('\u0a80' <= c <= '\u0aff' for c in text)
        font = pdf.custom_font if (pdf.use_custom_font and (has_gujarati or lang_code == 'gu')) else 'Arial'
        
        # If using Arial, we MUST clean the text
        if font == 'Arial':
            # Replace non-latin-1 characters with ?
            text = str(text).encode('latin-1', 'replace').decode('latin-1')
            
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
        
        # Avoid ° symbol to eliminate encoding issues, use "C"
        temp_val = f"{w.get('temp', '--')} C"
        
        put_text(f"{lbl_temp}: {temp_val} | {lbl_hum}: {w.get('humidity', '--')}%", font_size=10)
        pdf.ln(5)

    # Active Crops Section
    put_text(t.get('active_crop_fields', 'Active Crop Fields'), font_size=12, style='B')
    pdf.ln(2)
    
    if not active_crops:
        put_text(t.get('no_crops_added', 'No active crops registered.'), font_size=10, style='I')
    else:
        # Table Header
        header_font = pdf.custom_font if (pdf.use_custom_font and lang_code == 'gu') else 'Arial'
        pdf.set_font(header_font, 'B' if lang_code == 'en' else '', 10)
        pdf.set_fill_color(240, 240, 240)
        
        # Clean headers if Arial
        def h_txt(txt):
             if header_font == 'Arial': return txt.encode('latin-1', 'replace').decode('latin-1')
             return txt
             
        pdf.cell(50, 8, h_txt(t.get('crop_name_label', 'Crop Name')), 1, 0, 'C', 1)
        pdf.cell(30, 8, h_txt(t.get('area_label', 'Area (Ac)')), 1, 0, 'C', 1)
        pdf.cell(35, 8, h_txt(t.get('planting_date', 'Planting Date')), 1, 0, 'C', 1)
        pdf.cell(35, 8, h_txt(t.get('chlorophyll', 'Chlorophyll')), 1, 0, 'C', 1)
        pdf.cell(40, 8, h_txt('Health' if lang_code == 'en' else 'સ્વાસ્થ્ય'), 1, 1, 'C', 1)
        
        # Table Body
        for crop in active_crops:
            c_name = str(crop['crop_name'])
            
            # Cell 1: Name
            # Determine font for this specific cell based on content
            f = pdf.custom_font if (pdf.use_custom_font and any('\u0a80' <= c <= '\u0aff' for c in c_name)) else 'Arial'
            
            # If using Arial, clean the text to avoid Latin-1 error
            c_txt_final = c_name
            if f == 'Arial': 
                c_txt_final = c_name.encode('latin-1', 'replace').decode('latin-1')
            
            pdf.set_font(f, '', 9)
            pdf.cell(50, 8, c_txt_final, 1, 0, 'C')
            
            # Cell 2: Area (Always Arial/Numeric)
            pdf.set_font("Arial", '', 9)
            pdf.cell(30, 8, str(crop['area']), 1, 0, 'C')
            
            # Cell 3: Date (Always Arial/Numeric)
            pdf.cell(35, 8, str(crop['planting_date']), 1, 0, 'C')
            
            # Cell 4: Chlorophyll
            pdf.cell(35, 8, str(crop.get('chlorophyll', 'N/A')), 1, 0, 'C')
            
            # Cell 5: Health (May contain Gujarati)
            h_status = str(crop.get('health_status', 'N/A'))
            f = pdf.custom_font if (pdf.use_custom_font and any('\u0a80' <= c <= '\u0aff' for c in h_status)) else 'Arial'
            
            h_txt_final = h_status
            if f == 'Arial': 
                h_txt_final = h_status.encode('latin-1', 'replace').decode('latin-1')
                
            pdf.set_font(f, '', 9)
            pdf.cell(40, 8, h_txt_final, 1, 1, 'C')

    # Footer Note
    pdf.ln(10)
    note = "Note: Generated by Krishi-Mitra AI."
    if safe_mode:
        note += " (Safe Mode)"
    
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 5, note)
    
    # Return as clean bytes
    out = pdf.output()
    if isinstance(out, str):
        return out.encode('latin-1')
    return bytes(out)
