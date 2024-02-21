import requests

url = "https://whois-lookup-service.p.rapidapi.com/v1/getwhois"

querystring = {"url":"ntu.edu.sg"}

headers = {
	"X-RapidAPI-Key": "e3da8e7390msha58253180e1c0d6p19545fjsn2f1f4b97e2cd",
	"X-RapidAPI-Host": "whois-lookup-service.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())