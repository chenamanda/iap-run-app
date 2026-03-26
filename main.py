import os
import json
import base64
from flask import Flask, request

app = Flask(__name__)

def decode_iap_jwt(iap_jwt):
    """
    Manually decodes the JWT payload without signature verification 
    JUST for debugging attribute propagation.
    """
    try:
        # JWT is [header].[payload].[signature]
        parts = iap_jwt.split('.')
        if len(parts) != 3:
            return {"error": "Invalid JWT format"}
        
        # Base64 decode the middle part (payload)
        payload_b64 = parts[1]
        # Add padding if necessary
        missing_padding = len(payload_b64) % 4
        if missing_padding:
            payload_b64 += '=' * (4 - missing_padding)
            
        decoded_payload = base64.b64decode(payload_b64).decode('utf-8')
        return json.loads(decoded_payload)
    except Exception as e:
        return {"error": str(e)}

@app.route("/")
def index():
    # 1. Get the Raw JWT from IAP
    iap_jwt = request.headers.get('X-Goog-IAP-JWT-Assertion')
    user_email = request.headers.get('X-Goog-Authenticated-User-Email', 'Unknown')

    # 2. Decode the data to find SAML attributes
    decoded_data = decode_iap_jwt(iap_jwt) if iap_jwt else {}
    
    # 3. Specifically look for 'additional_claims' where SAML attributes live
    saml_attributes = decoded_data.get('additional_claims', {})
    
    # 4. For deep debugging, let's look at the FULL payload too
    full_payload_pretty = json.dumps(decoded_data, indent=4)
    saml_pretty = json.dumps(saml_attributes, indent=4)

    return f"""
    <html>
        <body style="font-family: sans-serif; padding: 40px; line-height: 1.6; color: #333;">
            <h1 style="color: #1a73e8;">IAP Attribute Debugger</h1>
            <p><b>Logged in as:</b> {user_email}</p>
            
            <hr>
            
            <h3 style="color: #d93025;">1. SAML Propagated Attributes</h3>
            <p>These are the attributes configured in Okta and enabled in IAP:</p>
            <pre style="background: #f1f3f4; padding: 15px; border-radius: 5px; border: 1px solid #ccc;">{saml_pretty}</pre>
            
            <h3 style="color: #1a73e8;">2. Full Raw JWT Payload</h3>
            <p>This is everything IAP knows about you right now:</p>
            <pre style="background: #202124; color: #34a853; padding: 15px; border-radius: 5px; overflow-x: auto;">{full_payload_pretty}</pre>
            
            <p style="margin-top: 20px;">
                <small>If <b>additional_claims</b> is empty, check your IAP "Attribute Propagation" settings in the GCP Console.</small>
            </p>
        </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))