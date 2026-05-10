"""
Telegram bot handlers — routes messages to the Claude agent.
"""
import logging
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.constants import ChatAction, ParseMode
from bot.agent import chat, reset_history, get_history_length
from config.settings import settings

logger = logging.getLogger(__name__)


def _is_allowed(user_id: int) -> bool:
    return settings.is_allowed(user_id)


async def _send_typing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING
    )


# ── Commands ──────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not _is_allowed(user.id):
        await update.message.reply_text("⛔ Accès non autorisé.")
        return

    name = settings.assistant_name
    await update.message.reply_text(
        f"👋 Bonjour {user.first_name} ! Je suis **{name}**, votre assistant personnel.\n\n"
        f"Je peux vous aider à :\n"
        f"• 🔍 Faire des recherches web\n"
        f"• 💼 Rédiger et publier des posts LinkedIn\n"
        f"• 📅 Créer des réunions et rendez-vous Google\n"
        f"• 📧 Envoyer des emails personnalisés\n"
        f"• 💬 Discuter et vous conseiller\n\n"
        f"Que puis-je faire pour vous ?",
        parse_mode=ParseMode.MARKDOWN,
    )


async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_allowed(update.effective_user.id):
        return
    reset_history(update.effective_user.id)
    await update.message.reply_text(
        "🔄 Conversation réinitialisée. On repart de zéro !",
        parse_mode=ParseMode.MARKDOWN,
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_allowed(update.effective_user.id):
        return
    name = settings.assistant_name
    await update.message.reply_text(
        f"**{name} — Guide rapide**\n\n"
        f"**Commandes :**\n"
        f"`/start` — Message de bienvenue\n"
        f"`/reset` — Effacer l'historique de conversation\n"
        f"`/status` — État de l'assistant\n"
        f"`/help` — Afficher cette aide\n\n"
        f"**Exemples de ce que vous pouvez demander :**\n"
        f"• _«Recherche les dernières nouvelles sur l'IA générative»_\n"
        f"• _«Rédige un post LinkedIn sur notre lancement produit»_\n"
        f"• _«Planifie une réunion avec jean@example.com demain à 14h»_\n"
        f"• _«Envoie un email de relance à marie@example.com»_\n"
        f"• _«Qu'est-ce qui est dans mon agenda cette semaine ?»_",
        parse_mode=ParseMode.MARKDOWN,
    )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_allowed(update.effective_user.id):
        return
    user_id = update.effective_user.id
    history_len = get_history_length(user_id)
    await update.message.reply_text(
        f"✅ **Assistant actif**\n"
        f"• Modèle : `{settings.claude_model}`\n"
        f"• Messages en mémoire : `{history_len}`\n"
        f"• Fuseau horaire : `{settings.timezone}`",
        parse_mode=ParseMode.MARKDOWN,
    )


# ── Message handler ───────────────────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not _is_allowed(user.id):
        await update.message.reply_text("⛔ Accès non autorisé.")
        return

    user_text = update.message.text
    if not user_text or not user_text.strip():
        return

    logger.info("User %s: %s", user.id, user_text[:80])

    # Show typing indicator
    await _send_typing(update, context)

    try:
        reply = await chat(user_id=user.id, user_message=user_text)
    except Exception as e:
        logger.error("Agent error for user %s: %s", user.id, e)
        reply = (
            "😕 Une erreur inattendue s'est produite. Veuillez réessayer dans quelques instants."
        )

    # Telegram Markdown can fail on special chars — fall back to plain text
    try:
        await update.message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)
    except Exception:
        await update.message.reply_text(reply)


# ── App builder ───────────────────────────────────────────────────────────────

def build_application() -> Application:
    app = Application.builder().token(settings.telegram_bot_token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return app


async def set_bot_commands(app: Application) -> None:
    await app.bot.set_my_commands([
        BotCommand("start", "Démarrer l'assistant"),
        BotCommand("help", "Aide et exemples"),
        BotCommand("status", "État de l'assistant"),
        BotCommand("reset", "Effacer la conversation"),
    ])
