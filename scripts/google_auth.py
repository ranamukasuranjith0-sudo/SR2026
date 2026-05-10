#!/usr/bin/env python3
"""
One-time Google OAuth2 authentication script.
Run this once to generate config/google_token.json
"""
import os
import sys

# Make sure we can import from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_auth_oauthlib.flow import InstalledAppFlow
from config.settings import settings

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
]


def main():
    creds_path = settings.google_credentials_path
    token_path = settings.google_token_path

    if not os.path.exists(creds_path):
        print(f"❌ Fichier credentials introuvable : {creds_path}")
        print(
            "   → Allez sur https://console.cloud.google.com, créez un projet,\n"
            "     activez Calendar API et Gmail API, puis téléchargez\n"
            "     les credentials OAuth2 (type: Desktop) dans ce chemin."
        )
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
    creds = flow.run_local_server(port=0)

    os.makedirs(os.path.dirname(token_path), exist_ok=True)
    with open(token_path, "w") as f:
        f.write(creds.to_json())

    print(f"✅ Token sauvegardé dans {token_path}")
    print("   Vous pouvez maintenant démarrer le bot.")


if __name__ == "__main__":
    main()
