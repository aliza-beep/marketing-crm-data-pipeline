"""Send a correctly signed simulated CRM event to a locally running receiver."""
import hashlib
import hmac
import json
import os
import urllib.request

body = json.dumps({"event_type": "lead.created", "lead_id": "SIM-WEBHOOK-001",
                   "note": "simulated portfolio event"}).encode()
secret = os.getenv("WEBHOOK_SECRET", "development-only-secret")
signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
request = urllib.request.Request("http://127.0.0.1:8000/webhooks/crm", data=body,
                                 headers={"Content-Type": "application/json",
                                          "X-Webhook-Signature": f"sha256={signature}"},
                                 method="POST")
print(urllib.request.urlopen(request, timeout=10).read().decode())

