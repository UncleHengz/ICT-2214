import pathlib
import textwrap

import google.generativeai as genai

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import fonts

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

def generative_ai():
  GOOGLE_API_KEY="AIzaSyBxwe1A407v5fpn5I5gPrzQT5TGX-P614E"

  genai.configure(api_key=GOOGLE_API_KEY)

  model = genai.GenerativeModel('gemini-pro')
  response = model.generate_content("This domain is facebook.com. Does it belong to this category computers_electronics_and_technology/social_networks_and_online_communities? Yes or no. Why?", stream=True)

  for chunk in response:
    print(chunk.text)
    print("_"*80)

def add_section(pdf_canvas, title, content, y_position):
    # Set font to bold
    pdf_canvas.setFont("Helvetica-Bold", 12)

    # Add a section heading
    pdf_canvas.drawCentredString(300, y_position, title)
    y_position -= 40  # Adjust vertical position for content

    # Set font back to regular
    pdf_canvas.setFont("Helvetica", 12)

    # Add content to the section
    for line in content:
        pdf_canvas.drawString(50, y_position, line)
        y_position -= 30  # Adjust vertical position for each line

    return y_position  # Return updated vertical position for the next section

def create_pdf_report():
    domain_name = "www.google.com"
    file_path = f"Report_{domain_name}.pdf"
    pdf_canvas = canvas.Canvas(file_path, pagesize=letter)
    
    # Register the bold font
    pdf_canvas.setFont("Helvetica-Bold", 15)

    # Title
    y_position = 750  # Initial vertical position
    pdf_canvas.drawCentredString(300, y_position, f"Analysis of {domain_name}")
    y_position -= 40  # Adjust vertical position for the title

    # Set font back to regular
    pdf_canvas.setFont("Helvetica", 12)

    # Section 1: Domain Analysis
    section_title = "Domain Analysis"
    section_content = ["This is the content of section 1."]
    y_position = add_section(pdf_canvas, section_title, section_content, y_position)

    # Section 2: Content Comparison
    section_title = "Content Comparison"
    section_content = ["This is the content of section 2."]
    y_position = add_section(pdf_canvas, section_title, section_content, y_position)

    # Section 3: Link Analysis
    section_title = "Link Analysis"
    section_content = ["This is the content of section 3."]
    y_position = add_section(pdf_canvas, section_title, section_content, y_position)

    # Section 4: Search Engine Status
    section_title = "Search Engine Status"
    section_content = ["This is the content of section 4."]
    y_position = add_section(pdf_canvas, section_title, section_content, y_position)

    # Section 5: Final Conclusion
    section_title = "Final Conclusion"
    section_content = ["This is the content of section 5."]
    y_position = add_section(pdf_canvas, section_title, section_content, y_position)

    pdf_canvas.save()
    print(f"PDF Report created successfully at: {file_path}")

if __name__ == "__main__":
  generative_ai()
  # create_pdf_report()
