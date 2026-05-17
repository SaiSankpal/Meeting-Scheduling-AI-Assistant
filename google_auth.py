from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
import os
from config import settings

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_credentials():
    creds = None
    token_file = settings.GOOGLE_TOKEN_FILE
    credentials_file = settings.GOOGLE_CREDENTIALS_FILE

    # Try to load existing token
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        except Exception as e:
            print(f"Error loading token: {e}")
            # Delete invalid token file
            if os.path.exists(token_file):
                os.remove(token_file)
            creds = None

    # Check if credentials are valid
    if not creds or not creds.valid:
        # Try to refresh if expired
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Save refreshed token
                with open(token_file, "w") as token:
                    token.write(creds.to_json())
                return creds
            except RefreshError as e:
                print(f"Token refresh failed: {e}")
                # Delete invalid token file
                if os.path.exists(token_file):
                    os.remove(token_file)
                creds = None
            except Exception as e:
                print(f"Error refreshing token: {e}")
                # Delete invalid token file
                if os.path.exists(token_file):
                    os.remove(token_file)
                creds = None

        # If no valid credentials, start OAuth flow
        if not creds:
            if not os.path.exists(credentials_file):
                raise FileNotFoundError(
                    f"credentials.json not found. Please download it from Google Cloud Console."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file,
                SCOPES,
            )

            creds = flow.run_local_server(port=0)

            # Save new token
            with open(token_file, "w") as token:
                token.write(creds.to_json())

    return creds
    
      
