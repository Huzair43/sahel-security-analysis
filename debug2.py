import requests
from config.settings import get_settings

# Get token
s = get_settings()
response = requests.post(
    s.acled_token_url,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data={
        "username":   s.acled_username,
        "password":   s.acled_password,
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
url = f"{s.acled_base_url}&country=Burkina Faso:OR:country=Mali&limit=5"
r = requests.get(url, headers=headers)
print(f"  Status: {r.json().get('status')}")
data = r.json().get("data", [])
countries = list(set([d.get("country") for d in data]))
print(f"  Countries found: {countries}\n")

# Test 2: URL encodée manuellement avec %20 et sans encoding requests
print("Test 2: Manually percent-encoded URL...")
url2 = f"{s.acled_base_url}&country=Burkina%20Faso%3AOR%3Acountry%3DMali&limit=5"
r2 = requests.get(url2, headers=headers)
print(f"  Status: {r2.json().get('status')}")
data2 = r2.json().get("data", [])
countries2 = list(set([d.get("country") for d in data2]))
print(f"  Countries found: {countries2}\n")

# Test 3 — Separate requests per country
print("Test 3: Burkina Faso alone...")
url3 = f"{s.acled_base_url}&country=Burkina Faso&limit=5"
r3 = requests.get(url3, headers=headers)
print(f"  Status: {r3.json().get('status')}")
data3 = r3.json().get("data", [])
countries3 = list(set([d.get("country") for d in data3]))
print(f"  Countries found: {countries3}\n")

print("Test 4: Mali alone...")
url4 = f"{s.acled_base_url}&country=Mali&limit=5"
r4 = requests.get(url4, headers=headers)
print(f"  Status: {r4.json().get('status')}")
data4 = r4.json().get("data", [])
countries4 = list(set([d.get("country") for d in data4]))
print(f"  Countries found: {countries4}\n")
