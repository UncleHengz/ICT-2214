import google.generativeai as genai

def gen_ai(query):
  GOOGLE_API_KEY="AIzaSyBxwe1A407v5fpn5I5gPrzQT5TGX-P614E"

  genai.configure(api_key=GOOGLE_API_KEY)

  model = genai.GenerativeModel('gemini-pro')
  
  response = model.generate_content(query)

  for chunk in response:
    print(chunk.text)
    print("_"*80)
    
  return response
  
