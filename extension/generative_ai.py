import pathlib
import textwrap

import google.generativeai as genai

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

GOOGLE_API_KEY="AIzaSyBxwe1A407v5fpn5I5gPrzQT5TGX-P614E"

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("Conditions to determine if a site is phishing site?", stream=True)

for chunk in response:
  print(chunk.text)
  print("_"*80)