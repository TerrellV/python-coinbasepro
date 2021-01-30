import requests, time, hmac, hashlib, base64
from requests.auth import AuthBase


class Auth(AuthBase):

    def __init__(self, api_key, secret, passphrase):
        self.api_key = api_key
        self.secret = secret
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())

        message = (
            timestamp
            + request.method
            + request.path_url
            + (request.body or '')
        )

        hmac_key = base64.b64decode(self.secret)

        signature = hmac.new(
            hmac_key,
            message.encode('utf-8'),
            hashlib.sha256
        )

        signature_b64 = base64.b64encode(signature.digest())

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })

        return request