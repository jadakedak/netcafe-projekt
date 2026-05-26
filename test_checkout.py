import requests

BASE_URL = "http://127.0.0.1:5000"

session = requests.Session()

# Step 2: send the checkout request
checkout = session.post(f"{BASE_URL}/api/checkout", json={
    "price_total": 50,
    "quantity_total": 1,
    "item": "4f7df6df-969c-4cad-b873-7ea60550b74f"
})
print("Status:", checkout.status_code)
print("Response:", checkout.text if checkout.text else "(empty - redirected to login)")
