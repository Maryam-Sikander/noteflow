import json
import os
import re
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import blue, black
from exa_py import Exa
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Register custom fonts
pdfmetrics.registerFont(TTFont('Regular', 'fonts/AnonymousPro-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Bold', 'fonts/AnonymousPro-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Italic', 'fonts/AnonymousPro-Italic.ttf'))

class ReportPDF:
    def __init__(self, title):
        self.title = title
        self.memory_buffer = BytesIO()
        self.pdf_canvas = canvas.Canvas(self.memory_buffer, pagesize=letter)
        self.pdf_canvas.setTitle(title)
        self.page_width, self.page_height = letter

    def add_page_numbering(self, page_number):
        self.pdf_canvas.setFont('Regular', 10)
        self.pdf_canvas.drawRightString(self.page_width - 72, 0.5 * inch, f"Page {page_number}")
        self.pdf_canvas.line(72, 0.6 * inch, self.page_width - 72, 0.6 * inch)

    def render_text(self, content, x_position, y_position, font_size=12, spacing=14, indentation=0):
        def split_text(text):
            patterns = [r'\*\*(.*?)\*\*', r'\*(.*?)\*', r'(https?://\S+)']
            start_pos = 0
            for match in re.finditer('|'.join(patterns), text):
                if start_pos < match.start():
                    yield text[start_pos:match.start()], 'Regular', black
                if match.group().startswith('**'):
                    yield match.group()[2:-2], 'Bold', black
                elif match.group().startswith('*') and not match.group().startswith('**'):
                    yield match.group()[1:-1], 'Italic', black
                elif re.match(r'https?://', match.group()):
                    yield match.group(), 'Italic', blue
                start_pos = match.end()
            if start_pos < len(text):
                yield text[start_pos:], 'Regular', black

        cursor_x = x_position + indentation
        cursor_y = y_position
        max_line_width = self.page_width - 2 * 72 - indentation
        for chunk, style, color in split_text(content):
            self.pdf_canvas.setFont(style, font_size)
            self.pdf_canvas.setFillColor(color)
            
            words = chunk.split()
            for word in words:
                word_width = self.pdf_canvas.stringWidth(word, self.pdf_canvas._fontname, font_size)
                if cursor_x + word_width > x_position + max_line_width:
                    cursor_y -= spacing
                    cursor_x = x_position + indentation
                self.pdf_canvas.drawString(cursor_x, cursor_y, word)
                cursor_x += word_width + self.pdf_canvas.stringWidth(' ', self.pdf_canvas._fontname, font_size)
            
            self.pdf_canvas.setFillColor(black)

        return x_position, cursor_y - spacing

    def generate_pdf(self, text_content):
        page_count = 1
        y_position = self.page_height - 1.5 * inch
        paragraphs = text_content.split("\n")
        bullet_point = u"\u2022"
        list_index = 1

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            if paragraph.startswith("### ") and y_position < self.page_height - 2 * inch:
                self.add_page_numbering(page_count)
                self.pdf_canvas.showPage()
                page_count += 1
                y_position = self.page_height - inch

            if y_position < 2 * inch:
                self.add_page_numbering(page_count)
                self.pdf_canvas.showPage()
                page_count += 1
                y_position = self.page_height - inch

            if paragraph.startswith("### "):
                y_position -= 0.5 * inch
                self.pdf_canvas.setFont('Bold', 18)
                self.pdf_canvas.drawString(72, y_position, paragraph[4:].strip())
                y_position -= 0.3 * inch
                self.pdf_canvas.line(72, y_position, self.page_width - 72, y_position)
                y_position -= 0.4 * inch
            elif paragraph.startswith("**"):
                y_position -= 0.3 * inch
                _, y_position = self.render_text(paragraph, 72, y_position, 14)
            elif paragraph.startswith("* "):
                paragraph = f"**{list_index}.** {paragraph[2:]}"
                list_index += 1
                _, y_position = self.render_text(paragraph, 72, y_position, 12, 14, 10)
            elif paragraph.startswith("  + ") or paragraph.startswith("  - "):
                paragraph = f"{bullet_point} {paragraph[4:]}"
                _, y_position = self.render_text(paragraph, 72, y_position, 12, 14, 20)
            else:
                _, y_position = self.render_text(paragraph, 72, y_position)

            y_position -= 0.1 * inch

        self.add_page_numbering(page_count)
        self.pdf_canvas.save()
        self.memory_buffer.seek(0)
        return self.memory_buffer.getvalue()

def generate_summary(formatted_transcript, system_instruction, url):
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
        try:
            result = exa.find_similar_and_contents(url, num_results=5, text=False)
            return result
        except Exception as e:
            print(f"Error fetching similar content: {e}")
            return []

    def extract_titles_and_urls(search_response):
        formatted_results = []
        if search_response:
            for item in search_response.results:
                title = item.title
                url = item.url
                formatted_results.append(f"**Title:** {title}\n**URL:** {url}")
        return formatted_results

    try:
        summary = generate_gemini_content(formatted_transcript, system_instruction)
    except Exception as e:
        print(f"Error generating summary: {e}")
        summary = "Couldn't generate summary for the given video."

    try:
        search_response = fetch_similar_content(url)
        similar_content = extract_titles_and_urls(search_response)
    except Exception as e:
        print(f"Error fetching similar content: {e}")
        similar_content = []

    combined_content = summary + "\n\n### Check out the Similar Content\n" + "\n\n".join(similar_content)
    
    return combined_content
