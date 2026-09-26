import requests

url = "https://www.ryanair.com/api/views/locate/3/airports/en/active"

response = requests.get(url, timeout=30)
response.raise_for_status()

data = response.json()

airports = {}

for airport in data:
    if airport["iataCode"] in ["MXP", "LIN", "BGY"]:
        print(
            airport["name"],
            airport["iataCode"],
            airport["cityCode"]
        )
