import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from bot.tools.google_calendar import _get_credentials
from config.settings import settings


def _gmail_service():
    return build("gmail", "v1", credentials=_get_credentials())


def send_email(
    to: str,
    subject: str,
    body: str,
    cc: str = "",
    html: bool = False,
) -> str:
    """Send an email via Gmail."""
    try:
        service = _gmail_service()

        if html:
            msg = MIMEMultipart("alternative")
            msg.attach(MIMEText(body, "html", "utf-8"))
        else:
            msg = MIMEMultipart()
            msg.attach(MIMEText(body, "plain", "utf-8"))

        msg["To"] = to
        msg["Subject"] = subject
        if cc:
            msg["Cc"] = cc
        if settings.google_user_email:
            msg["From"] = settings.google_user_email

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        service.users().messages().send(userId="me", body={"raw": raw}).execute()

        recipients = to
        if cc:
            recipients += f" (cc: {cc})"
        return f"✅ Email envoyé à **{recipients}**\nSujet : _{subject}_"

    except RuntimeError as e:
        return f"❌ {e}"
    except Exception as e:
        return f"❌ Erreur Gmail : {e}"


TOOL_DEFINITION = {
    "name": "send_email",
    "description": (
        "Envoie un email personnalisé via Gmail. "
        "IMPORTANT : présente toujours l'aperçu complet de l'email (destinataire, sujet, corps) "
        "à l'utilisateur pour validation avant d'appeler cet outil."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "to": {
                "type": "string",
                "description": "Adresse email du destinataire principal.",
            },
            "subject": {
                "type": "string",
                "description": "Objet de l'email.",
            },
            "body": {
                "type": "string",
                "description": "Corps complet de l'email, rédigé de manière personnalisée et professionnelle.",
            },
            "cc": {
                "type": "string",
                "description": "Adresse(s) email en copie (séparées par des virgules, optionnel).",
                "default": "",
            },
        },
        "required": ["to", "subject", "body"],
    },
}
