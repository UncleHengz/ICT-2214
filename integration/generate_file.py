from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import fonts
import io
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def to_markdown(text):
	text = text.replace('•', '  *')
	return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

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

def create_pdf_report(domain_name, details):
	print(details["domain"])
	print(details["database"])
	print(details["ssl"])
	print(details["search"])
	pdf_buffer = io.BytesIO()
	pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=letter)

	# Register the bold font
	pdf_canvas.setFont("Helvetica-Bold", 15)

	# Title
	y_position = 750  # Initial vertical position
	pdf_canvas.drawCentredString(300, y_position, f"Analysis of '{domain_name}'")
	y_position -= 40  # Adjust vertical position for the title

	# Set font back to regular
	pdf_canvas.setFont("Helvetica", 12)

	# Section 1: Domain Analysis
	section_title = "Domain Analysis"
	section_content = ["This is the content of section 1."]
	y_position = add_section(pdf_canvas, section_title, section_content, y_position)
 
 	# Section 2: Database Analysis
	section_title = "Database Analysis"
	database_content_p1 = "Current domain is not detected as malicious. "
	database_content_p2 = "Other domains on the website are not detected as malicious"
	if details["database"]["Domain"] == True:
		database_content_p1 = "Current domain is detected as malicious. "
	if details["database"]["Other Domains"] == True:
		database_content_p2 = "Other domains on the website are detected as malicious"
	final_content = database_content_p1+database_content_p2
	section_content = [final_content] 
	y_position = add_section(pdf_canvas, section_title, section_content, y_position)

	# Define a style for the content paragraphs
	styles = getSampleStyleSheet()
	content_style = styles["Normal"]

	# Section 3: SSL Analysis
	section_title = "SSL Analysis"
	ssl_content_p1 = "Secure Socket Layer (SSL) does not exist on the domain. "
	ssl_content_p2 = "The certificate is by an invalid Certificate Authority. "
	ssl_content_p3 = "Certificate is not issued. "
	if details["ssl"]["SSL"] == True:
		ssl_content_p1 = "Secure Socket Layer (SSL) exist on the domain. "
	if details["ssl"]["Authorised CA"] == True:
		ssl_content_p2 = "The certificate is by a valid Certificate Authority. "
	if details["ssl"]["Issued By"] != "":
		ssl_content_p3 = f"Issued by {details['ssl']['Issued By']}"
	# section_content = ["This is the content of section 2."]
	ssl_content = ssl_content_p1 + ssl_content_p2 + ssl_content_p3 
 
	# Create a Paragraph object with the SSL content and apply the content style
	ssl_paragraph = Paragraph(ssl_content, content_style)

	# Add the Paragraph object to the section content list
	section_content = [ssl_paragraph]

	# Add the section to the PDF canvas
	y_position = add_section(pdf_canvas, section_title, section_content, y_position)
 
	section_content = [ssl_content]
	y_position = add_section(pdf_canvas, section_title, section_content, y_position)
 
 	# Section 4: Search Engine Analysis
	section_title = "Search Engine Analysis"
	section_content = ["This is the content of section 4."]
	y_position = add_section(pdf_canvas, section_title, section_content, y_position)

	# # Section 5: Content Analysis
	# section_title = "Content Analysis"
	# section_content = ["This is the content of section 4."]
	# y_position = add_section(pdf_canvas, section_title, section_content, y_position)

	# Section 6: Final Conclusion
	section_title = "Final Conclusion"
	section_content = ["This is the content of section 5."]
	y_position = add_section(pdf_canvas, section_title, section_content, y_position)

	pdf_canvas.save()
	pdf_content = pdf_buffer.getvalue()
	pdf_buffer.close()
	# print(f"PDF Report created successfully at: {file_path}")

	# print(pdf_content)
	return pdf_content