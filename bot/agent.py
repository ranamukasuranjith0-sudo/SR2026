"""
Claude-powered AI agent with tool use and per-user conversation memory.
"""
import json
import logging
from collections import defaultdict
from anthropic import Anthropic
from bot.tools import ALL_TOOLS, TOOL_HANDLERS
from config.settings import settings
from config.prompts import get_system_prompt

logger = logging.getLogger(__name__)

# In-memory conversation history keyed by Telegram user_id
_history: dict[int, list[dict]] = defaultdict(list)

MAX_HISTORY = 40  # keep last N messages per user

client = Anthropic(api_key=settings.anthropic_api_key)


def _trim_history(user_id: int) -> None:
    history = _history[user_id]
    if len(history) > MAX_HISTORY:
        # Always keep pairs (user/assistant), drop oldest
        _history[user_id] = history[-MAX_HISTORY:]


def _execute_tool(tool_name: str, tool_input: dict) -> str:
    handler = TOOL_HANDLERS.get(tool_name)
    if not handler:
        return f"Outil inconnu : {tool_name}"
    try:
        return handler(tool_input)
    except Exception as e:
        logger.error("Tool %s failed: %s", tool_name, e)
        return f"Erreur lors de l'exécution de l'outil {tool_name} : {e}"


async def chat(user_id: int, user_message: str) -> str:
    """Process a user message through the Claude agent and return a response."""
    _history[user_id].append({"role": "user", "content": user_message})
    _trim_history(user_id)

    messages = list(_history[user_id])

    # Agentic loop — Claude may call multiple tools in sequence
    while True:
        response = client.messages.create(
            model=settings.claude_model,
            max_tokens=4096,
            system=get_system_prompt(),
            tools=ALL_TOOLS,
            messages=messages,
        )

        # Collect text blocks for a potential final answer
        text_blocks = [b.text for b in response.content if b.type == "text"]
        tool_uses = [b for b in response.content if b.type == "tool_use"]

        if response.stop_reason == "end_turn" or not tool_uses:
            # No more tool calls — final answer
            final = "\n\n".join(text_blocks).strip()
            # Add assistant turn to history
            _history[user_id].append({"role": "assistant", "content": response.content})
            _trim_history(user_id)
            return final or "Je n'ai pas pu générer de réponse. Pouvez-vous reformuler ?"

        # Append assistant message with tool calls to messages
        messages.append({"role": "assistant", "content": response.content})

        # Execute each tool and build tool_result blocks
        tool_results = []
        for tool_use in tool_uses:
            logger.info("Calling tool: %s with %s", tool_use.name, tool_use.input)
            result = _execute_tool(tool_use.name, tool_use.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": result,
            })

        messages.append({"role": "user", "content": tool_results})

        # Continue loop — Claude will process results and either respond or call more tools


def reset_history(user_id: int) -> None:
    """Clear conversation history for a user."""
    _history.pop(user_id, None)


def get_history_length(user_id: int) -> int:
    return len(_history.get(user_id, []))
