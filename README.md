# Assistant Telegram IA — Guide d'installation client

Un assistant personnel intelligent disponible sur Telegram, propulsé par Claude (Anthropic).

## Fonctionnalités

| Capacité | Commande naturelle |
|---|---|
| 🔍 Recherche web | *«Cherche les dernières actus sur X»* |
| 💼 Post LinkedIn | *«Rédige un post LinkedIn sur notre lancement»* |
| 📅 Réunion Google | *«Planifie un call avec alice@ex.com demain à 14h»* |
| 📆 Rendez-vous | *«Crée un RDV chez le médecin vendredi à 9h»* |
| 📧 Email personnalisé | *«Envoie un email de relance à bob@ex.com»* |
| 💬 Discussion | Tout autre message — conversation naturelle |

---

## Installation (5 étapes)

### 1. Prérequis

- Python 3.12+ ou Docker
- Un compte Telegram
- Clés API (voir section suivante)

### 2. Cloner et configurer

```bash
git clone <url-du-repo>
cd SR2026
cp .env.example .env
# Éditez .env avec vos clés
```

### 3. Obtenir les clés API

#### Telegram Bot
1. Ouvrez [@BotFather](https://t.me/botfather) sur Telegram
2. Tapez `/newbot` et suivez les instructions
3. Copiez le token dans `TELEGRAM_BOT_TOKEN`

#### Anthropic (Claude)
1. Créez un compte sur [console.anthropic.com](https://console.anthropic.com)
2. Générez une clé API → `ANTHROPIC_API_KEY`

#### Tavily (recherche web)
1. Inscrivez-vous sur [tavily.com](https://tavily.com)
2. Copiez votre clé → `TAVILY_API_KEY`

#### LinkedIn
1. Créez une app sur [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Activez les scopes `w_member_social` et `r_liteprofile`
3. Générez un access token → `LINKEDIN_ACCESS_TOKEN`
4. Récupérez votre URN de profil → `LINKEDIN_PERSON_URN`

#### Google (Calendar + Gmail)
1. Allez sur [Google Cloud Console](https://console.cloud.google.com)
2. Créez un projet, activez **Google Calendar API** et **Gmail API**
3. Créez des identifiants OAuth2 (type: Application de bureau)
4. Téléchargez le JSON → `config/google_credentials.json`
5. Lancez l'authentification :
```bash
python scripts/google_auth.py
```
6. Un navigateur s'ouvre → autorisez l'accès → `config/google_token.json` est créé

### 4. Lancer le bot

**Avec Docker (recommandé) :**
```bash
docker-compose up -d
```

**Sans Docker :**
```bash
pip install -r requirements.txt
python -m bot.main
```

### 5. Tester sur Telegram

Ouvrez votre bot sur Telegram et tapez `/start`.

---

## Personnalisation

Tout se configure dans le fichier `.env` :

| Variable | Description |
|---|---|
| `ASSISTANT_NAME` | Prénom de l'assistant (ex: *Alex*, *Sara*, *Max*) |
| `ASSISTANT_TONE` | `professional` / `friendly` / `casual` |
| `ASSISTANT_LANGUAGE` | `fr` (français) ou `en` (anglais) |
| `TIMEZONE` | Fuseau horaire (ex: `Europe/Paris`, `America/Montreal`) |
| `ALLOWED_TELEGRAM_IDS` | IDs autorisés (laisser vide = accès libre) |

---

## Architecture

```
bot/
├── main.py               # Point d'entrée
├── handlers.py           # Gestion des messages Telegram
├── agent.py              # Agent Claude avec tool use + mémoire
└── tools/
    ├── search.py         # Recherche Tavily
    ├── linkedin.py       # Posts LinkedIn
    ├── google_calendar.py # Google Calendar
    └── gmail.py          # Gmail
config/
├── settings.py           # Chargement de la configuration
└── prompts.py            # Personnalité de l'assistant
scripts/
└── google_auth.py        # Authentification Google (une fois)
```

## Commandes Telegram

| Commande | Action |
|---|---|
| `/start` | Message de bienvenue |
| `/help` | Aide et exemples |
| `/status` | État de l'assistant |
| `/reset` | Effacer l'historique de conversation |
