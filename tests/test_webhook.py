import hashlib
import hmac

from marketing_pipeline.webhook import valid_signature


def test_webhook_hmac_validation():
    body, secret = b'{"event_type":"lead.created"}', "test-secret"
    signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    assert valid_signature(body, f"sha256={signature}", secret)
    assert not valid_signature(body, "bad", secret)

