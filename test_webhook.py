import requests

url = "https://tableful-facility-zone.ngrok-free.dev/webhook"

params = {
    "hub.mode": "subscribe",
    "hub.verify_token": "my_secret_token",
    "hub.challenge": "TESTCHALLENGE"
}

r = requests.get(url, params=params)

print("Status:", r.status_code)
print("Response:", r.text)