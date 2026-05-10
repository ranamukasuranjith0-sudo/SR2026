from bot.tools import search, linkedin, google_calendar, gmail

ALL_TOOLS = [
    search.TOOL_DEFINITION,
    linkedin.TOOL_DEFINITION,
    google_calendar.CREATE_EVENT_TOOL,
    google_calendar.LIST_EVENTS_TOOL,
    gmail.TOOL_DEFINITION,
]

TOOL_HANDLERS = {
    "web_search": lambda args: search.web_search(**args),
    "create_linkedin_post": lambda args: linkedin.create_linkedin_post(**args),
    "create_calendar_event": lambda args: google_calendar.create_event(**args),
    "list_calendar_events": lambda args: google_calendar.list_events(**args),
    "send_email": lambda args: gmail.send_email(**args),
}
