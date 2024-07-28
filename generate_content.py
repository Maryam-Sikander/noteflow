import json
import os
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import blue, black
import re
from exa_py import Exa
import google.generativeai as genai
from dotenv import load_dotenv
import base64
# Load environment variables
load_dotenv()

from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import blue, black
import re
from io import BytesIO

# Register custom fonts
pdfmetrics.registerFont(TTFont('Regular', 'fonts/AnonymousPro-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Bold', 'fonts/AnonymousPro-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Italic', 'fonts/AnonymousPro-Italic.ttf'))

class PDFDocument:
    def __init__(self, title):
        self.buffer = BytesIO()
        self.canvas = canvas.Canvas(self.buffer, pagesize=letter)
        self.canvas.setTitle(title)
        self.width, self.height = letter

    def add_page_number(self, page_num):
        self.canvas.setFont('Regular', 10)
        self.canvas.drawRightString(self.width - 72, 0.5 * inch, f"Page {page_num}")
        self.canvas.line(72, 0.6 * inch, self.width - 72, 0.6 * inch)

    def draw_text(self, text, x, y, size=12, line_height=14, indent=0):
        def get_chunks(text):
            patterns = [r'\*\*(.*?)\*\*', r'\*(.*?)\*', r'(https?://\S+)']
            cursor = 0
            for match in re.finditer('|'.join(patterns), text):
                if cursor < match.start():
                    yield text[cursor:match.start()], 'Regular', black
                if match.group().startswith('**'):
                    yield match.group()[2:-2], 'Bold', black
                elif match.group().startswith('*') and not match.group().startswith('**'):
                    yield match.group()[1:-1], 'Italic', black
                elif re.match(r'https?://', match.group()):
                    yield match.group(), 'Italic', blue
                cursor = match.end()
            if cursor < len(text):
                yield text[cursor:], 'Regular', black

        cursor_x = x + indent
        cursor_y = y
        line_width = self.width - 2 * 72 - indent
        for chunk, style, color in get_chunks(text):
            self.canvas.setFont(style, size)
            self.canvas.setFillColor(color)
            
            words = chunk.split()
            for word in words:
                word_width = self.canvas.stringWidth(word, self.canvas._fontname, size)
                if cursor_x + word_width > x + line_width:
                    cursor_y -= line_height
                    cursor_x = x + indent
                self.canvas.drawString(cursor_x, cursor_y, word)
                cursor_x += word_width + self.canvas.stringWidth(' ', self.canvas._fontname, size)
            
            self.canvas.setFillColor(black)

        return x, cursor_y - line_height

    def create_pdf(self, content):
        page_num = 1
        y = self.height - 1.5 * inch
        sections = content.split("\n")
        bullet = u"\u2022"
        list_counter = 1

        for section in sections:
            section = section.strip()  # Remove leading and trailing spaces
            if not section:
                continue

            if section.startswith("### ") and y < self.height - 2 * inch:
                self.add_page_number(page_num)
                self.canvas.showPage()
                page_num += 1
                y = self.height - inch

            if y < 2 * inch:
                self.add_page_number(page_num)
                self.canvas.showPage()
                page_num += 1
                y = self.height - inch

            if section.startswith("### "):
                y -= 0.5 * inch
                self.canvas.setFont('Bold', 18)
                self.canvas.drawString(72, y, section[4:].strip())
                y -= 0.3 * inch
                self.canvas.line(72, y, self.width - 72, y)
                y -= 0.4 * inch
            elif section.startswith("**"):
                y -= 0.3 * inch
                _, y = self.draw_text(section, 72, y, 14)
            elif section.startswith("* "):
                section = f"**{list_counter}.** {section[2:]}"
                list_counter += 1
                _, y = self.draw_text(section, 72, y, 12, 14, 10)
            elif section.startswith("  + ") or section.startswith("  - "):
                section = f"{bullet} {section[4:]}"
                _, y = self.draw_text(section, 72, y, 12, 14, 20)
            else:
                _, y = self.draw_text(section, 72, y)

            y -= 0.1 * inch

        self.add_page_number(page_num)
        self.canvas.save()
        self.buffer.seek(0)
        return self.buffer.getvalue()


def generate_combined_content(formatted_transcript, system_instruction, url):
    exa_api_key = os.getenv("EXA_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    genai.configure(api_key=GOOGLE_API_KEY)
    exa = Exa(api_key=exa_api_key)

    def generate_gemini_content(formatted_transcript, system_instruction):
        formatted_transcript_str = json.dumps(formatted_transcript)
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(system_instruction + formatted_transcript_str)
        return response.text

    def fetch_similar_content(url):
        result = exa.find_similar_and_contents(url, num_results=5, text=False)
        return result

    def extract_titles_and_urls(search_response):
        formatted_results = []
        for item in search_response.results:
            title = item.title
            url = item.url
            formatted_results.append(f"**Title:** {title}\n**URL:** {url}")
        return formatted_results

    summary = generate_gemini_content(formatted_transcript, system_instruction)
    search_response = fetch_similar_content(url)
    similar_content = extract_titles_and_urls(search_response)
    combined_content = summary + "\n\n### Check out the Similar Content\n" + "\n\n".join(similar_content)
    
    return combined_content
