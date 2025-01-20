# Python standard libraries
import os

# Third party libraries
from flask import request

from oauthlib.oauth2 import WebApplicationClient
import requests


# Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "13256348917-k29q8fpfoblkan04mfadpr8fe6vafkg6.apps.googleusercontent.com")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "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")
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# OAuth2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

def auth():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/get_user_info",
        scope=["openid", "email", "profile"],
    )
    
    return request_uri

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()
