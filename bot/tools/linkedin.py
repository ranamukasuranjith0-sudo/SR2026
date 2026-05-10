import requests
from config.settings import settings


LINKEDIN_API_BASE = "https://api.linkedin.com/v2"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.linkedin_access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }


def create_linkedin_post(content: str, visibility: str = "PUBLIC") -> str:
    """Publish a post on LinkedIn."""
    if not settings.linkedin_access_token or not settings.linkedin_person_urn:
        return "❌ LinkedIn non configuré. Renseignez LINKEDIN_ACCESS_TOKEN et LINKEDIN_PERSON_URN dans .env"

    payload = {
        "author": settings.linkedin_person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": content},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": visibility},
    }

    resp = requests.post(
        f"{LINKEDIN_API_BASE}/ugcPosts",
        headers=_headers(),
        json=payload,
        timeout=30,
    )

    if resp.status_code in (200, 201):
        post_id = resp.headers.get("x-restli-id", "inconnu")
        return f"✅ Post LinkedIn publié avec succès ! ID : {post_id}"
    else:
        return f"❌ Erreur LinkedIn ({resp.status_code}) : {resp.text}"


TOOL_DEFINITION = {
    "name": "create_linkedin_post",
    "description": (
        "Rédige et publie un post sur LinkedIn pour l'utilisateur. "
        "IMPORTANT : présente toujours le contenu à l'utilisateur pour validation avant d'appeler cet outil."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "Le texte complet du post LinkedIn, prêt à être publié.",
            },
            "visibility": {
                "type": "string",
                "enum": ["PUBLIC", "CONNECTIONS"],
                "description": "Visibilité du post: PUBLIC (tout le monde) ou CONNECTIONS (relations uniquement).",
                "default": "PUBLIC",
            },
        },
        "required": ["content"],
    },
}
