from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import fonts
import io
from generative_ai import gen_ai

def generate_summary(details):
	# Construct the query string using f-strings
	query = f"""
	Please provide details for each analysis metric:

	Domain Analysis (WHOIS date, anti-virus score, category):
	1.1 WHOIS date: {details['domain']['Age']}
	1.2 Total Anti-virus vendor score: {details['domain']['Anti-Virus Score']}
	1.3 Category from VirusTotal detected as suspicious: {details['domain']['Category']}

	Database Analysis (Domain, domains on the website):
	2.1 Domain detected as malicious: {details['database']['Domain']}
	2.2 Other domains on website detected as malicious: {details['database']['Other Domains']}

	SSL Analysis (SSL, Authorised CA):
	3.1 SSL exist: {details['ssl']['SSL']}
	3.2 Authorised CA: {details['ssl']['Authorised CA']}

	Search Engine Analysis (Site index, Google Safe Browsing, Similar web):
	4.1 Site Index suspicious number of results: {details['search']['Site Index']}
	4.2 Google Safe Browsing of URL: {details['search']['Google Safe Browsing']}
	4.3 Similarweb suspiciousness of URL: {details['search']['Similar Web']}

	Content Analysis (Check for misspelled words): {details['content']['Result']}
	"""
	response = gen_ai(query)
 
	return response

def generate_final_conclusion(pdf_canvas, summary, max_width, section_title, y_position):
    # Add section title
    pdf_canvas.setFont("Helvetica-Bold", 12)
    pdf_canvas.drawCentredString(300, y_position, section_title)
    y_position -= 40  # Adjust vertical position for content

    # Set font back to regular
    pdf_canvas.setFont("Helvetica", 12)

    # Split summary into sentences and wrap each sentence
    sentences = summary.split('. ')  # Split at period followed by space
    for sentence in sentences:
        # Wrap the sentence to fit within the maximum width
        wrapped_sentence = textwrap.fill(sentence, width=max_width)
        pdf_canvas.drawString(50, y_position, wrapped_sentence)
        y_position -= 30  # Adjust vertical position for each line

    return y_position  # Return updated vertical position for the next section

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
		# Check if the content will overflow the page
		if y_position < 50:
		# If overflow, start a new page
			pdf_canvas.showPage()
			pdf_canvas.setFont("Helvetica", 12)
			y_position = 750  # Reset vertical position for new page
			pdf_canvas.drawCentredString(300, y_position, title)
			y_position -= 40  # Adjust vertical position for content
		pdf_canvas.drawString(50, y_position, line)
		y_position -= 30  # Adjust vertical position for each line

	return y_position  # Return updated vertical position for the next section

def create_pdf_report(domain_name, details):
	try:
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
		domain_result_p1 = f"WHOIS date is {details['domain']['Age']}"
		domain_result_p2 = "Anti-virus tools did not find the domain suspicious. "
		domain_result_p3 = "Domain website's category is legitimate"
		if details['domain']['Anti-Virus Score'] > 0:
			domain_result_p2 = f"Anti-virus tools has detected domain to be suspicious with score {details['domain']['Anti-Virus Score']}"
		if details['domain']['Category'] == True:
			domain_result_p3 = "Domain website's category is flagged as suspicious."
		section_content = ["WHOIS: " + domain_result_p1, "Anti-Virus: " + domain_result_p2, "Domain Category: " + domain_result_p3, "Malicious: " + str(details["domain"]["Result"])]
		y_position = add_section(pdf_canvas, section_title, section_content, y_position)
  
		# Section 2: Database Analysis
		section_title = "Database Analysis"
		database_content_p1 = "Current domain is not detected as malicious."
		database_content_p2 = "Other domains on the website are not detected as malicious."
		if details["database"]["Domain"] == True:
			database_content_p1 = "Current domain is detected as malicious."
		if details["database"]["Other Domains"] == True:
			database_content_p2 = "Other domains on the website are detected as malicious."
		section_content = ["Current Domain: " + database_content_p1, "Other Domains: " + database_content_p2, "Malicious: " + str(details['database']['Result'])] 
		y_position = add_section(pdf_canvas, section_title, section_content, y_position)
  
		# Section 3: SSL Analysis
		section_title = "SSL Analysis"
		ssl_content_p1 = "Secure Socket Layer (SSL) exist on the domain."
		ssl_content_p2 = "The certificate is by a valid Certificate Authority."
		ssl_content_p3 = f"Issued by {details['ssl']['Issued By']}"
		if details["ssl"]["SSL"] == True:
			ssl_content_p1 = "Secure Socket Layer (SSL) does not exist on the domain."
		if details["ssl"]["Authorised CA"] == True:
			ssl_content_p2 = "The certificate is by an invalid Certificate Authority."
		if details["ssl"]["Issued By"] == "":
			ssl_content_p3 = "Certificate is not issued."
		section_content = ["SSL: " + ssl_content_p1, "Validity of Certificate Authority: " + ssl_content_p2, "Issued By: " + ssl_content_p3, "Malicious: " + str(details['ssl']['Result'])]
		y_position = add_section(pdf_canvas, section_title, section_content, y_position)
		
		section_title = "Search Engine Analysis"
		search_engine_p1 = "Results from site indexing shows valid number of results results."
		search_engine_p2 = "Google Safe Browsing has found URL to be safe."
		search_engine_p3 = "Similar Web has not found any suspicious statistics."
		if details["search"]["Site Index"] == True:
			search_engine_p1 = "Results from site indexing shows low or no results."
		if details["search"]["Google Safe Browsing"] == True:
			search_engine_p2 = "Google Safe Browsing has found URL to be malicious."
		if details["search"]["Similar Web"] == True:
			search_engine_p3 = "Similar Web has found suspicious statistics."
		section_content = ["Site Index: " + search_engine_p1, "Google Safe Browsing: " + search_engine_p2, "Similar Web: " + search_engine_p3, "Malicious: " + str(details['search']['Result'])]
		y_position = add_section(pdf_canvas, section_title, section_content, y_position)

		# Section 5: Content Analysis
		section_title = "Content Analysis"
		content = "Low numbers of misspelled words"
		section_content = ["Mispelled Words: " + content, "Percentage of Mispelled Words: " + details['content']['Percentage Wrongly Spelled'], "Explanation: ", details['content']['Reason'], "Malicious: " + str(details['content']['Result'])]
		y_position = add_section(pdf_canvas, section_title, section_content, y_position)

		# Section 6: Final Conclusion
		section_title = "Final Conclusion"
		summary = generate_summary(details)

		# Split the summary into lines with proper word wrapping
		lines = []
		for line in summary.text.split("\n"):
			words = line.split()
			wrapped_line = ""
			for word in words:
				if pdf_canvas.stringWidth(wrapped_line + " " + word, "Helvetica", 12) < 500:  # Adjust 500 to your desired width
					wrapped_line += " " + word
				else:
					lines.append(wrapped_line.strip())
					wrapped_line = word
			lines.append(wrapped_line.strip())

		# Add the section title to the PDF canvas
		pdf_canvas.setFont("Helvetica-Bold", 12)
		pdf_canvas.drawString(50, y_position, section_title)
		y_position -= 40  # Adjust vertical position for content

		# Add each line of the summary with word wrapping
		pdf_canvas.setFont("Helvetica", 12)
		for line in lines:
			# Check if the content will overflow the page
			if y_position < 50:
				# If overflow, start a new page
				pdf_canvas.showPage()
				y_position = 750  # Reset vertical position for new page
				# Add section title on new page
				pdf_canvas.setFont("Helvetica-Bold", 12)
				pdf_canvas.drawString(50, y_position, section_title)
				y_position -= 40  # Adjust vertical position for content
				# Set font back to regular
				pdf_canvas.setFont("Helvetica", 12)
			# Add the line of the summary
			pdf_canvas.drawString(50, y_position, line)
			y_position -= 20  # Adjust vertical position for the next line

		# Update the vertical position for the next section
		y_position -= 20  # Add extra spacing between sections

		pdf_canvas.save()
		pdf_content = pdf_buffer.getvalue()
		pdf_buffer.close()
  
		return pdf_content
	except Exception as e:
		print("Error at generate_file:", e)
     