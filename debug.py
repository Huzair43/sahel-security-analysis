import requests
from config.settings import get_settings

# Step 1: Get token
print("Step 1: Authenticating...")
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
print("Token obtained (masked).\n")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type":  "application/json",
}

BASE = s.acled_base_url

# Step 2: Simplest possible request (no filters at all)
print("Step 2: Minimal request (limit=5, no filters)...")
r = requests.get(BASE, params={"limit": 5}, headers=headers)
print(f"  HTTP status : {r.status_code}")
print(f"  API status  : {r.json().get('status')}")
print(f"  Count       : {r.json().get('count')}")
print()

# Step 3: Single country, no fields filter
print("Step 3: Single country request (Burkina Faso, no fields filter)...")
r = requests.get(BASE, params={"country": "Burkina Faso", "limit": 5}, headers=headers)
print(f"  HTTP status : {r.status_code}")
print(f"  API status  : {r.json().get('status')}")
print(f"  Count       : {r.json().get('count')}")
print()

# Step 4: Multi-country syntax
print("Step 4: Multi-country syntax...")
r = requests.get(
    BASE,
    params={"country": "Burkina Faso:OR:country=Mali", "limit": 5},
    headers=headers,
)
print(f"  HTTP status : {r.status_code}")
print(f"  API status  : {r.json().get('status')}")
print(f"  Count       : {r.json().get('count')}")
print()

# Step 5: Add fields filter
print("Step 5: Single country WITH fields filter...")
r = requests.get(
    BASE,
    params={
        "country": "Burkina Faso",
        "limit":   5,
        "fields":  "event_id_cnty|event_date|event_type|country|fatalities",
    },
    headers=headers,
)
print(f"  HTTP status : {r.status_code}")
print(f"  API status  : {r.json().get('status')}")
print(f"  Message     : {r.json().get('message', 'none')}")
print()

print("Diagnostic complete. Share the output above.")
