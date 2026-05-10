import json
from tavily import TavilyClient
from config.settings import settings


_client: TavilyClient | None = None


def _get_client() -> TavilyClient:
    global _client
    if _client is None:
        _client = TavilyClient(api_key=settings.tavily_api_key)
    return _client


def web_search(query: str, max_results: int = 5, search_depth: str = "advanced") -> str:
    """Perform a web search and return formatted results."""
    client = _get_client()
    response = client.search(
        query=query,
        search_depth=search_depth,
        max_results=max_results,
        include_answer=True,
    )

    results = []

    if response.get("answer"):
        results.append(f"**Synthèse :** {response['answer']}\n")

    for i, r in enumerate(response.get("results", []), 1):
        title = r.get("title", "Sans titre")
        url = r.get("url", "")
        content = r.get("content", "")[:300]
        results.append(f"{i}. **{title}**\n   {content}...\n   🔗 {url}")

    return "\n\n".join(results) if results else "Aucun résultat trouvé."


TOOL_DEFINITION = {
    "name": "web_search",
    "description": (
        "Effectue une recherche web pour trouver des informations récentes sur n'importe quel sujet. "
        "Utilise cet outil quand l'utilisateur demande des informations sur l'actualité, des données "
        "récentes, ou tout sujet nécessitant une recherche externe."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "La requête de recherche, formulée de manière précise.",
            },
            "max_results": {
                "type": "integer",
                "description": "Nombre maximum de résultats (1-10, défaut: 5).",
                "default": 5,
            },
        },
        "required": ["query"],
    },
}
