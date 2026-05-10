import os
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from config.settings import settings

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
]


def _get_credentials() -> Credentials:
    creds = None
    token_path = settings.google_token_path

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, "w") as f:
                f.write(creds.to_json())
        else:
            raise RuntimeError(
                "Token Google invalide ou absent. Lancez `python scripts/google_auth.py` pour vous authentifier."
            )
    return creds


def _calendar_service():
    return build("calendar", "v3", credentials=_get_credentials())


def _parse_datetime(dt_str: str, tz: ZoneInfo) -> datetime:
    """Parse ISO or natural datetime string."""
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(dt_str, fmt)
            return dt.replace(tzinfo=tz)
        except ValueError:
            continue
    raise ValueError(f"Format de date non reconnu : {dt_str}")


def create_event(
    title: str,
    start_datetime: str,
    duration_minutes: int = 60,
    description: str = "",
    attendees: list[str] | None = None,
    location: str = "",
    meet_link: bool = True,
) -> str:
    """Create a Google Calendar event."""
    try:
        service = _calendar_service()
        tz = ZoneInfo(settings.timezone)

        start = _parse_datetime(start_datetime, tz)
        end = start + timedelta(minutes=duration_minutes)

        event: dict = {
            "summary": title,
            "description": description,
            "location": location,
            "start": {"dateTime": start.isoformat(), "timeZone": settings.timezone},
            "end": {"dateTime": end.isoformat(), "timeZone": settings.timezone},
        }

        if attendees:
            event["attendees"] = [{"email": e.strip()} for e in attendees]

        if meet_link:
            event["conferenceData"] = {
                "createRequest": {
                    "requestId": f"meet-{title[:10]}-{start.timestamp():.0f}",
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            }

        created = service.events().insert(
            calendarId="primary",
            body=event,
            conferenceDataVersion=1 if meet_link else 0,
            sendUpdates="all" if attendees else "none",
        ).execute()

        meet_url = ""
        if meet_link and created.get("conferenceData", {}).get("entryPoints"):
            for ep in created["conferenceData"]["entryPoints"]:
                if ep.get("entryPointType") == "video":
                    meet_url = ep.get("uri", "")
                    break

        result = (
            f"✅ Événement créé : **{title}**\n"
            f"📅 {start.strftime('%d/%m/%Y à %H:%M')} ({duration_minutes} min)\n"
        )
        if location:
            result += f"📍 {location}\n"
        if meet_url:
            result += f"🎥 Google Meet : {meet_url}\n"
        if attendees:
            result += f"👥 Participants notifiés : {', '.join(attendees)}\n"
        result += f"🔗 [Voir dans Calendar]({created.get('htmlLink', '')})"
        return result

    except RuntimeError as e:
        return f"❌ {e}"
    except Exception as e:
        return f"❌ Erreur Google Calendar : {e}"


def list_events(days_ahead: int = 7) -> str:
    """List upcoming events."""
    try:
        service = _calendar_service()
        tz = ZoneInfo(settings.timezone)
        now = datetime.now(tz)
        end = now + timedelta(days=days_ahead)

        events_result = service.events().list(
            calendarId="primary",
            timeMin=now.isoformat(),
            timeMax=end.isoformat(),
            maxResults=15,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        events = events_result.get("items", [])
        if not events:
            return f"📅 Aucun événement prévu dans les {days_ahead} prochains jours."

        lines = [f"📅 **Agenda — {days_ahead} prochains jours :**\n"]
        for ev in events:
            start_raw = ev["start"].get("dateTime", ev["start"].get("date", ""))
            try:
                if "T" in start_raw:
                    start_dt = datetime.fromisoformat(start_raw)
                    time_str = start_dt.strftime("%d/%m à %H:%M")
                else:
                    time_str = datetime.strptime(start_raw, "%Y-%m-%d").strftime("%d/%m (journée)")
            except Exception:
                time_str = start_raw
            lines.append(f"• {time_str} — **{ev.get('summary', 'Sans titre')}**")

        return "\n".join(lines)

    except RuntimeError as e:
        return f"❌ {e}"
    except Exception as e:
        return f"❌ Erreur Google Calendar : {e}"


CREATE_EVENT_TOOL = {
    "name": "create_calendar_event",
    "description": (
        "Crée un événement dans Google Calendar. Peut ajouter un lien Google Meet et inviter des participants. "
        "Confirme toujours les détails (titre, date/heure, durée, participants) avant d'appeler cet outil."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Titre de l'événement ou de la réunion."},
            "start_datetime": {
                "type": "string",
                "description": "Date et heure de début au format ISO ou 'YYYY-MM-DD HH:MM'.",
            },
            "duration_minutes": {
                "type": "integer",
                "description": "Durée en minutes (défaut: 60).",
                "default": 60,
            },
            "description": {"type": "string", "description": "Description ou ordre du jour."},
            "attendees": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Liste des adresses email des participants.",
            },
            "location": {"type": "string", "description": "Lieu de l'événement (optionnel)."},
            "meet_link": {
                "type": "boolean",
                "description": "Ajouter un lien Google Meet (défaut: true).",
                "default": True,
            },
        },
        "required": ["title", "start_datetime"],
    },
}

LIST_EVENTS_TOOL = {
    "name": "list_calendar_events",
    "description": "Affiche les prochains événements du calendrier Google de l'utilisateur.",
    "input_schema": {
        "type": "object",
        "properties": {
            "days_ahead": {
                "type": "integer",
                "description": "Nombre de jours à afficher (défaut: 7).",
                "default": 7,
            }
        },
        "required": [],
    },
}
