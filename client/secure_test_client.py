import time
import uuid
import hmac
import hashlib
import json
import requests

# ===============================
# CONFIG – replace these values
# ===============================

API_URL = "http://127.0.0.1:8000/v1/merchants/secure-test"
PUBLIC_KEY = "pk_cb9641002bcc27d9ca3c5b76c925fbae"
SECRET_KEY = "b668486192351ad221914e383930165b21b068184d5ed4c6defbba47d4b87962"

# ===============================
# Payload
# ===============================

payload = {
    "amount": 100
}

payload_json = json.dumps(payload, separators=(",", ":"))

# ===============================
# Security headers
# ===============================

timestamp = int(time.time())
nonce = str(uuid.uuid4())

signature = hmac.new(
    SECRET_KEY.encode(),
    payload_json.encode(),
    hashlib.sha256
).hexdigest()

headers = {
    "Content-Type": "application/json",
    "X-Public-Key": PUBLIC_KEY,
    "X-Signature": signature,
    "X-Timestamp": str(timestamp),
    "X-Nonce": nonce,
}

# ===============================
# Send request
# ===============================

response = requests.post(
    API_URL,
    json=payload,  # <-- use `json=` instead of `data=`
    headers=headers,
)


print("\n--- REQUEST ---")
print("Payload:", payload_json)
print("Headers:")
for k, v in headers.items():
    if "KEY" in k or "Signature" in k:
        print(f"{k}: ****")
    else:
        print(f"{k}: {v}")

print("\n--- RESPONSE ---")
print("Status Code:", response.status_code)
print("Response JSON:", response.json())
