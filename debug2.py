import requests
from config.config import ACLED_USERNAME, ACLED_PASSWORD, ACLED_TOKEN_URL

# Get token
response = requests.post(
    ACLED_TOKEN_URL,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data={
        "username":   ACLED_USERNAME,
        "password":   ACLED_PASSWORD,
        "grant_type": "password",
        "client_id":  "acled",
    },
)
token = response.json()["access_token"]
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type":  "application/json",
}

# Test 1: test URL
print("Test 1: Hardcoded URL with OR syntax...")
url = "https://acleddata.com/api/acled/read?_format=json&country=Burkina Faso:OR:country=Mali&limit=5"
r = requests.get(url, headers=headers)
print(f"  Status: {r.json().get('status')}")
data = r.json().get("data", [])
countries = list(set([d.get("country") for d in data]))
print(f"  Countries found: {countries}\n")

# Test 2: URL encodée manuellement avec %20 et sans encoding requests
print("Test 2: Manually percent-encoded URL...")
url2 = "https://acleddata.com/api/acled/read?_format=json&country=Burkina%20Faso%3AOR%3Acountry%3DMali&limit=5"
r2 = requests.get(url2, headers=headers)
print(f"  Status: {r2.json().get('status')}")
data2 = r2.json().get("data", [])
countries2 = list(set([d.get("country") for d in data2]))
print(f"  Countries found: {countries2}\n")

# Test 3 — Separate requests per country
print("Test 3: Burkina Faso alone...")
url3 = "https://acleddata.com/api/acled/read?_format=json&country=Burkina Faso&limit=5"
r3 = requests.get(url3, headers=headers)
print(f"  Status: {r3.json().get('status')}")
data3 = r3.json().get("data", [])
countries3 = list(set([d.get("country") for d in data3]))
print(f"  Countries found: {countries3}\n")

print("Test 4: Mali alone...")
url4 = "https://acleddata.com/api/acled/read?_format=json&country=Mali&limit=5"
r4 = requests.get(url4, headers=headers)
print(f"  Status: {r4.json().get('status')}")
data4 = r4.json().get("data", [])
countries4 = list(set([d.get("country") for d in data4]))
print(f"  Countries found: {countries4}\n")