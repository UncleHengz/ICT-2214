import google.generativeai as genai

def gen_ai(query):
  GOOGLE_API_KEY="AIzaSyBxwe1A407v5fpn5I5gPrzQT5TGX-P614E"

  genai.configure(api_key=GOOGLE_API_KEY)

  model = genai.GenerativeModel('gemini-pro')
  
  response = model.generate_content(query)
  # sentence = response.text

  # # Find the index of the period to split the sentence
  # period_index = sentence.find('.')
  # # Split the sentence into two parts based on the period
  # malicious_part = sentence[:period_index].strip()  # Include the period and remove leading/trailing whitespaces
  # description_part = sentence[period_index + 1:].strip()  # Exclude the period and remove leading/trailing whitespaces
  # print(sentence)
  # result_details = {
  #   "Total Errors": total_errors,
  #   "Percentage Wrongly Spelled": percentage_wrongly_spelled,
  #   "Reason": description_part
  # }
  
  
  # if malicious_part == "Yes":
  #   return True, result_details
  # elif malicious_part == "No":
  #   return False, result_details

  for chunk in response:
    print(chunk.text)
    print("_"*80)
    
  return response
  
  # return None, ""
